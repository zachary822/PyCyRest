import functools
import logging
from typing import Dict, IO, List, Optional, Tuple

from lxml import etree

from pycyrest.base import ClientBase

__all__ = ['CyRest']

logger = logging.getLogger(__name__)


class CyRest(ClientBase):
    def __getattr__(self, item):
        func = super().__getattr__(item)

        @functools.wraps(func)
        def wrapper(**kwargs):
            result = func(**kwargs)

            try:
                if result['errors']:
                    raise ValueError(result['errors'])

                return result['data']  # get data from return object when possible
            except (KeyError, TypeError):
                return result

        return wrapper

    def add_vizmap(self, f):
        """
        Add vizmap to cytoscape

        :param f:
        :return:
        """
        title, defaults, mappings, dependencies = self.parse_vizmap(f)

        res = self.createStyle(body={
            'title': title,
            'defaults': defaults,
            'mappings': mappings
        })

        self.updateDependencies(name=res['title'], body=dependencies)

        return res

    def apply_vizmap(self, network_id: int, vizmap: Optional[IO] = None, style_name: Optional[str] = None):
        if vizmap is not None:
            res = self.add_vizmap(vizmap)
            style_name = res['title']

        if style_name is None:
            raise TypeError('Provide vizmap file or style name. Cannot both be None.')

        self.applyStyle(networkId=network_id, styleName=style_name)

    @staticmethod
    def parse_vizmap(f: IO) -> Tuple[str, List[Dict], List[Dict], List[Dict]]:
        defaults = []
        mappings = []
        dependencies = []

        tree = etree.parse(f)

        title = tree.find('visualStyle').attrib['name']

        for d in tree.iter('dependency'):
            dependencies.append({
                'visualPropertyDependency': d.attrib['name'],
                'enabled': d.attrib['value'] == 'true'
            })

        for vp in tree.iter('visualProperty'):
            if 'default' in vp.attrib:
                defaults.append({
                    'visualProperty': vp.attrib['name'],
                    'value': vp.attrib['default']
                })
            try:
                map_ele = vp[0]
                mapping = {
                    "mappingColumn": map_ele.attrib["attributeName"],
                    "mappingColumnType": map_ele.attrib["attributeType"].capitalize(),
                    "visualProperty": vp.attrib['name']
                }

                if map_ele.tag == 'passthroughMapping':
                    mapping["mappingType"] = "passthrough"

                elif map_ele.tag == 'discreteMapping':
                    mapping["mappingType"] = "discrete"
                    mapping["map"] = [{'key': entry.attrib['attributeValue'], 'value': entry.attrib['value']}
                                      for entry in map_ele.iter('discreteMappingEntry')]
                elif map_ele.tag == 'continuousMapping':
                    mapping["mappingType"] = "continuous"
                    mapping["points"] = [{
                        'value': float(point.attrib['attrValue']),
                        'equal': point.attrib['equalValue'],
                        'lesser': point.attrib['lesserValue'],
                        'greater': point.attrib['greaterValue']
                    } for point in map_ele.iter('continuousMappingPoint')]
                else:
                    raise ValueError(f"Invalid mapping type {map_ele.tag}")

                mappings.append(mapping)

            except IndexError:
                pass

        return title, defaults, mappings, dependencies
