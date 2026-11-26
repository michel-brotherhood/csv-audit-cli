import tempfile
import unittest
from pathlib import Path
from audit import audit


class AuditTest(unittest.TestCase):
    def make_file(self, content):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / 'example.csv'
        path.write_text(content, encoding='utf-8')
        return path

    def test_missing_duplicate_and_malformed(self):
        path = self.make_file('id,name\n1,Ana\n1,Ana\n2,\n3\n4,Bia,extra\n')
        self.assertEqual(audit(path), {
            'rows': 5, 'columns': ['id', 'name'], 'missing_by_column': {'id': 0, 'name': 2},
            'duplicate_rows': [3], 'malformed_rows': [5, 6], 'duplicate_basis': 'entire row'})

    def test_key_duplicate(self):
        path = self.make_file('id,name\n1,Ana\n1,Bia\n')
        self.assertEqual(audit(path, 'id')['duplicate_rows'], [3])

    def test_invalid_header(self):
        path = self.make_file('id,id\n1,2\n')
        with self.assertRaises(ValueError):
            audit(path)


if __name__ == '__main__':
    unittest.main()
