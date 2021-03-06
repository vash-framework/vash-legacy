from shutil import rmtree
from os.path import isdir

import pytest

from engine.models.node import Node
#
from engine.models.folders.page import Page
from engine.models.folders.bases.folder import Folder
from engine.models.folders.template import Template
from engine.models.folders.bases.resource import Resource
#
from engine.models.files.bases.file import File
from engine.models.files.json import JsonFile
from engine.models.files.meta import MetaFile
from engine.models.files.page_meta import PageMetaFile
from engine.models.files.template_meta import TemplateMetaFile
#
from engine.models.processors.minifier import Minifier
from engine.models.processors.bases.processor import Processor

TEST_ROOT = '/tmp/tests'

RELATIVE_PATH_A = 'the-holy-grail/french-castle'
RELATIVE_PATH_B = 'the-holy-grail/the-black-knight'

ABSOLUTE_PATH_A = f'{TEST_ROOT}/{RELATIVE_PATH_A}'
ABSOLUTE_PATH_B = f'{TEST_ROOT}/{RELATIVE_PATH_B}'

FILE_SUBCLASSES = [JsonFile]
JSON_FILE_SUBCLASSES = [MetaFile]
META_FILE_SUBCLASSES = [PageMetaFile, TemplateMetaFile]
FILE_CLASSES = [File] + FILE_SUBCLASSES + JSON_FILE_SUBCLASSES + META_FILE_SUBCLASSES

RESOURCE_SUBCLASSES = [Page, Template]
RESOURCE_CLASSES = [Resource] + RESOURCE_SUBCLASSES

FOLDER_CLASSES = [Folder] + RESOURCE_CLASSES

NODE_SUBCLASSES = FILE_CLASSES + FOLDER_CLASSES
NODE_CLASSES = [Node] + NODE_SUBCLASSES

PROCESSOR_SUBCLASSES = [Minifier]
PROCESSOR_CLASSES = [Processor] + PROCESSOR_SUBCLASSES


@pytest.fixture(autouse=True)
def monkey_patch_node_root(monkeypatch):
    for model in NODE_CLASSES:
        monkeypatch.setattr(
            model,
            'ROOT',
            f'{TEST_ROOT}{model.ROOT}',
            raising=True
        )


@pytest.fixture(autouse=True)
def remove_node_root(request):
    yield
    if isdir(TEST_ROOT):
        rmtree(TEST_ROOT)


@pytest.fixture
def relative_path():
    return RELATIVE_PATH_A


@pytest.fixture
def absolute_path():
    return ABSOLUTE_PATH_A


@pytest.fixture(params=[RELATIVE_PATH_A] + [ABSOLUTE_PATH_A])
def path(request):
    return request.param
