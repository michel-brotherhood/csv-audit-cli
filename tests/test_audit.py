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

    def test_disk_mode_matches_memory_mode(self):
        path = self.make_file('id,name\n1,Ana\n1,Bia\n2,\n2,\n3\n')
        self.assertEqual(audit(path, disk=True), audit(path))
        self.assertEqual(audit(path, 'id', disk=True), audit(path, 'id'))

    def test_disk_mode_many_rows(self):
        path = self.make_file('id,name\n' + ''.join(f'{n},Pessoa {n}\n' for n in range(10000)) + '9999,Pessoa 9999\n')
        result = audit(path, disk=True)
        self.assertEqual(result['rows'], 10001)
        self.assertEqual(result['duplicate_rows'], [10002])

    def test_invalid_header(self):
        path = self.make_file('id,id\n1,2\n')
        with self.assertRaises(ValueError):
            audit(path)


if __name__ == '__main__':
    unittest.main()
