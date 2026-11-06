import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import date
from scripts import update_stamps as stamps


class PostalParserTest(unittest.TestCase):
    def test_roc_date(self):
        self.assertEqual(stamps.roc_date('115/11/20至115/11/20'), date(2026, 11, 20))

    def test_venue_is_not_automatically_a_recipient(self):
        recipient, address, status = stamps.recipient_from_notes(
            '活動地點：臺中公園 (主辦局：臺中郵局)')
        self.assertEqual((recipient, address, status), ('', '', '待確認'))

    def test_explicit_recipient(self):
        recipient, address, status = stamps.recipient_from_notes(
            '臺中公園（郵件請寄:臺中集郵中心）（主辦局：臺中郵局）')
        self.assertEqual(recipient, '臺中集郵中心')
        self.assertFalse(address)
        self.assertIn('地址待確認', status)

    def test_extract_rows(self):
        html = '''<html><body><div>您查詢 115/11/20 ~ 115/12/05 的結果如下(共1筆)</div>
        <table><tr><td>115/11/20至115/11/20</td><td>臺中</td><td>寶可夢郵票</td>
        <td>臺中民權路郵局（郵件請寄:臺中民權路郵局）(主辦局:臺中郵局)</td>
        <td><a href="sz_stampmark_dtl.jsp?ID=507&amp;temp_sn=12345">戳圖</a></td></tr></table>
        </body></html>'''
        res = stamps.parse_rows(html, date(2026, 11, 20), date(2026, 12, 5))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['title'], '寶可夢郵票')
        self.assertEqual(res[0]['recipient'], '臺中民權路郵局')
        self.assertTrue(res[0]['official_url'].endswith('temp_sn=12345'))

    def test_file_signature(self):
        self.assertEqual(stamps.image_bytes(b'\xff\xd8\xffx'), '.jpg')
        self.assertIsNone(stamps.image_bytes(b'<html>error</html>'))


if __name__ == '__main__':
    unittest.main()
