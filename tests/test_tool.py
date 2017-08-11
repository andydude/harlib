from harlib.test_utils import TestUtils
from harlib.tool import har_sort
import six


class ToolTests(TestUtils):

    def setUp(self):
        pass

    def test_tool(self):
        filename = 'tests/data/test.har'
        writer = six.StringIO()
        with open(filename, 'r') as reader:
            har_sort(reader, writer)
        out = writer.getvalue()
        self.assertTrue(out.startswith('{'), out[:100])
