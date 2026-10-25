import os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from verify_syntax import verify_file,preprocess_luau

class NativeSyntaxRegressions(unittest.TestCase):
    def verify(self,code):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"test.luau"
            file.write_text(code,encoding="utf-8")
            return verify_file(file)[0]

    def test_continue_outside_loop_is_rejected(self):
        self.assertFalse(self.verify("continue"))

    def test_continue_string_is_preserved(self):
        source='local message="continue"; print(message)'
        self.assertEqual(preprocess_luau(source),source)
        self.assertTrue(self.verify(source))

    def test_luau_type_annotation_is_supported(self):
        self.assertTrue(self.verify("local value: number = 42"))

    def test_valid_continue_in_loop(self):
        self.assertTrue(self.verify("for i=1,5 do if i==2 then continue end print(i) end"))

    def test_missing_end_is_rejected(self):
        self.assertFalse(self.verify("local function broken()"))

    def test_missing_file_is_not_accepted(self):
        self.assertFalse(verify_file(Path("__file_that_does_not_exist__.luau"))[0])

    def test_missing_compiler_does_not_skip_validation(self):
        with patch.dict(os.environ,{"LUAU_COMPILER":"__missing_luau_compiler__"}):
            self.assertFalse(self.verify("print('valid')"))

if __name__=="__main__": unittest.main()

