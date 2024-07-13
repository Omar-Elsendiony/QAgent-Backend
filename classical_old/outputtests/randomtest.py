import unittest

# Example
def add(x: int, y: int)->int:
	return x + y



class TestClass(unittest.TestCase):
	def test_case_0(self):

		int_0=56
		int_1=12
		self.assertEqual(68,add(int_0,int_1))

	def test_case_1(self):

		int_0=82
		int_1=20
		self.assertEqual(102,add(int_0,int_1))

	def test_case_2(self):

		int_0=98
		int_1=1
		self.assertEqual(99,add(int_0,int_1))

	def test_case_3(self):

		int_0=45
		int_1=45
		self.assertEqual(90,add(int_0,int_1))

	def test_case_4(self):

		int_0=30
		int_1=89
		self.assertEqual(119,add(int_0,int_1))

	def test_case_5(self):

		int_0=19
		int_1=72
		self.assertEqual(91,add(int_0,int_1))

	def test_case_6(self):

		int_0=75
		int_1=68
		self.assertEqual(143,add(int_0,int_1))

	def test_case_7(self):

		int_0=94
		int_1=2
		self.assertEqual(96,add(int_0,int_1))

	def test_case_8(self):

		int_0=24
		int_1=52
		self.assertEqual(76,add(int_0,int_1))

	def test_case_9(self):

		int_0=34
		int_1=100
		self.assertEqual(134,add(int_0,int_1))

if __name__ == '__main__':
    unittest.main()
    