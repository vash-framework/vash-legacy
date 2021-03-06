from engine.utilities import merge_metas
from engine.models.files.meta import MetaFile
from engine.models.folders.template import Template


class PageCacheFile(MetaFile):
    INITIAL_KEYS = {
        'forward-relations': [],
        'backward-relations': [],
    }

    @property
    def templates(self):
        try:
            template_paths = self['template'].split(' > ')
        except KeyError:
            return []
        else:
            return [Template(path) for path in template_paths]

    @property
    def template_meta(self):
        meta = {}
        for template in self.templates:
            template_meta = template.meta.read()
            merge_metas(meta, template_meta)
        else:
            return meta
