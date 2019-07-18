from unittest import TestCase, main

from numpy.testing import assert_allclose

from cogent3 import LoadTree
from cogent3.draw.dendrogram import (
    CircularTreeGeometry,
    Dendrogram,
    SquareTreeGeometry,
)


__author__ = "Gavin Huttley"
__copyright__ = "Copyright 2007-2012, The Cogent Project"
__credits__ = ["Gavin Huttley"]
__license__ = "BSD-3"
__version__ = "2019.07.10a"
__maintainer__ = "Gavin Huttley"
__email__ = "gavin.huttley@anu.edu.au"
__status__ = "Alpha"


class TestDendro(TestCase):
    def test_geometry(self):
        """tree geometry class get_edge_names works"""
        tree = LoadTree(treestring="(a,b,(c,(d,e)e1)e2)")
        geom = SquareTreeGeometry(tree)
        series = [
            dict(tip1name="d", tip2name="c", clade=True, stem=False),
            dict(tip1name="d", tip2name="c", clade=True, stem=True),
            dict(tip1name="d", tip2name="c", clade=False, stem=True),
            dict(tip1name="d", tip2name="c", clade=True, stem=False, outgroup_name="e"),
            dict(tip1name="d", tip2name="c", clade=False, stem=True, outgroup_name="e"),
        ]
        for kwargs in series[-1:]:
            expect = tree.get_edge_names(**kwargs)
            got = geom.get_edge_names(**kwargs)
            self.assertEqual(got, expect)

    def test_get_edges(self):
        """returns edge names"""
        tree = LoadTree(treestring="(a,b,(c,(d,e)e1)e2)")
        dnd = Dendrogram(tree=tree)
        edges = dnd.get_edge_names("d", "c", clade=True, stem=False)
        self.assertEqual(set(edges), set(["c", "d", "e", "e1"]))

    def test_min_max_x_y(self):
        """correctly compute the min and max of x and y"""
        tree = LoadTree(treestring="(A:1,B:2,C:3)")
        geom = CircularTreeGeometry(tree)
        geom.propagate_properties()
        got = max(map(abs, [geom.min_x, geom.max_x]))
        expect = max(map(abs, [e.x for e in geom.postorder()]))
        assert_allclose(got, expect)
        got = max(map(abs, [geom.min_y, geom.max_y]))
        expect = max(map(abs, [e.y for e in geom.postorder()]))
        assert_allclose(got, expect)

    def test_length_attr_valid(self):
        """Tests whether setting a custom length attribute provides valid x values"""
        tree = LoadTree(
            treestring="((a:0.1,b:0.25):0.1,(c:0.02,d:0.03, (e:0.035, f:0.04):0.15):0.3 , g:0.3)"
        )
        geom = SquareTreeGeometry(tree, length_attr="custom")
        geom.params["custom"] = 1

        for e in geom.preorder():
            if e.is_root():
                continue
            e.params["custom"] = e.parent.params.get("custom", 1) * 2
        geom.propagate_properties()

        # .x attribute is cumulative from the root, which we have set to 1
        # for 'custom', e.g. a.x == 2 + 4 == 6
        func = geom.get_node_matching_name
        xs = [
            func("root").x,
            func("a").x,
            func("b").x,
            func("c").x,
            func("d").x,
            func("e").x,
            func("f").x,
            func("g").x,
        ]

        # Root x resets to 0 so any assigned value is always discarded
        self.assertEqual(xs, [0, 6, 6, 6, 6, 14, 14, 2])


if __name__ == "__main__":
    main()