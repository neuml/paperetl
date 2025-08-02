"""
Optional module tests
"""

import sys
import unittest


# pylint: disable=C0415
class TestOptional(unittest.TestCase):
    """
    Optional tests. Simulates optional dependencies not being installed.
    """

    @classmethod
    def setUpClass(cls):
        """
        Simulate optional packages not being installed
        """

        modules = ["elasticsearch"]

        # Get handle to all currently loaded paperetl modules
        modules = modules + [key for key in sys.modules if key.startswith("paperetl")]
        cls.modules = {module: None for module in modules}

        # Replace loaded modules with stubs. Save modules for later reloading
        for module in cls.modules:
            if module in sys.modules:
                cls.modules[module] = sys.modules[module]

            # Remove paperetl modules. Set optional dependencies to None to prevent reloading.
            if "paperetl" in module:
                if module in sys.modules:
                    del sys.modules[module]
            else:
                sys.modules[module] = None

    def testElasticsearch(self):
        """
        Test missing training dependencies
        """

        from paperetl.elastic import Elastic

        with self.assertRaises(ImportError):
            Elastic(None, None)
