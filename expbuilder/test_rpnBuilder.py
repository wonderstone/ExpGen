import unittest
from expbuilder.op import Operator, OPType
from expbuilder.rpnBuilder import GetArityDict, MaskActionSpace, MaskOPSpace
from expbuilder.rpnBuilder import GetActionSpace, ConstantToken, FeatureToken, DeltaTimeToken, OperatorToken, SEP_TOKEN

class TestGetArityDict(unittest.TestCase):
    def test_empty_ops(self):
        ops = {}
        expected = {}
        result, _ = GetArityDict(ops)
        self.assertEqual(result, expected)

    def test_single_op(self):
        ops = {'+': (lambda x, y: x + y, 2)}
        expected = {2: ['+']}
        result, tmp = GetArityDict(ops)
        self.assertEqual(result, expected)

    def test_multiple_ops_same_arity(self):
        ops = {
            '+': (lambda x, y: x + y, 2),
            '-': (lambda x, y: x - y, 2)
        }
        expected = {2: ['+', '-']}
        result, _ = GetArityDict(ops)
        self.assertEqual(result, expected)

    def test_multiple_ops_different_arity(self):
        ops = {
            '+': (lambda x, y: x + y, 2),
            'neg': (lambda x: -x, 1)
        }
        expected = {2: ['+'], 1: ['neg']}
        result, _ = GetArityDict(ops)
        self.assertEqual(result, expected)

    def test_complex_ops(self):
        ops = {
            '+': (lambda x, y: x + y, 2),
            'neg': (lambda x: -x, 1),
            'sum3': (lambda x, y, z: x + y + z, 3),
            '-': (lambda x, y: x - y, 2)
        }
        expected = {2: ['+','-'], 1: ['neg'], 3: ['sum3']}
        result, _ = GetArityDict(ops)
        self.assertEqual(result, expected)

class TestGetActionSpace(unittest.TestCase):
    def test_empty_inputs(self):
        Constants = None
        Features = None
        DeltaTimes = None
        CSOperators = None
        expected = ['SEP']
        result = GetActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators=None)
        # only check the values of the two lists are the same
        for i in range(len(result)):
            self.assertEqual(result[i], expected[i])


    def test_constants_only(self):
        Constants = [1.0, 2.0]
        Features = None
        DeltaTimes = None
        Operators = None
        expected = ["1.0", "2.0", 'SEP']
        result = GetActionSpace(Constants, Features, DeltaTimes, Operators, TSOperators=None)
        for i in range(len(result)):
            self.assertEqual(result[i], expected[i])

    def test_features_only(self):
        Constants = None
        Features = ["$feature1", "$feature2"]
        DeltaTimes = None
        Operators = None
        expected = ["$feature1", "$feature2", 'SEP']
        result = GetActionSpace(Constants, Features, DeltaTimes,Operators, TSOperators=None)
        for i in range(len(result)):
            self.assertEqual(result[i], expected[i])

    def test_deltatimes_only(self):
        Constants = None
        Features = None
        DeltaTimes = [1, 2]
        Operators = None
        expected = ['1', '2', 'SEP']
        result = GetActionSpace(Constants, Features, DeltaTimes, Operators, TSOperators=None)
        for i in range(len(result)):
            self.assertEqual(result[i], expected[i])

    def test_operators_only(self):
        Constants = None
        Features = None
        DeltaTimes = None
        op1 = Operator(name="+", Optype=OPType.CS, callable=(lambda x, y: x + y), argTypeList=[float, float])
        op2 = Operator(name="-", Optype=OPType.CS, callable=(lambda x, y: x - y), argTypeList=[float, float])
        Operators = [op1.name, op2.name]
        TSOperators = ["ref"]
        expected = ["+", "-", "ref", 'SEP']
        result = GetActionSpace(Constants, Features, DeltaTimes, CSOperators=Operators, TSOperators=TSOperators)
        for i in range(len(result)):
            self.assertEqual(result[i], expected[i])

    def test_all_inputs(self):
        Constants = [1.0]
        Features = ["$feature1"]
        DeltaTimes = [1]
        Operators = ["+"]
        TSOperators = ["ref"]
        expected = [
            '1.0',
            '$feature1',
            '1',
            '+',
            'ref',
            'SEP'
        ]
        result = GetActionSpace(Constants, Features, DeltaTimes, Operators, TSOperators)
        for i in range(len(result)):
            self.assertEqual(result[i], expected[i])    
      
class TestMaskOPSpace(unittest.TestCase):
    def test_empty_operators(self):
        func_arity_dict = {}
        ValidOPDict = {"Max": 2}
        Operators = []
        expected = []
        result = MaskOPSpace(func_arity_dict, ValidOPDict, Operators)
        self.assertEqual(result, expected)

    def test_single_operator_valid(self):
        func_arity_dict = {'+': 2}
        ValidOPDict = {"Max": 2}
        Operators = ['+']
        expected = [True]
        result = MaskOPSpace(func_arity_dict, ValidOPDict, Operators)
        self.assertEqual(result, expected)

    def test_single_operator_invalid(self):
        func_arity_dict = {'+': 3}
        ValidOPDict = {"Max": 2}
        Operators = ['+']
        expected = [False]
        result = MaskOPSpace(func_arity_dict, ValidOPDict, Operators)
        self.assertEqual(result, expected)

    def test_multiple_operators_all_valid(self):
        func_arity_dict = {'+': 2, '-': 2}
        ValidOPDict = {"Max": 2}
        Operators = ['+', '-']
        expected = [True, True]
        result = MaskOPSpace(func_arity_dict, ValidOPDict, Operators)
        self.assertEqual(result, expected)

    def test_multiple_operators_some_invalid(self):
        func_arity_dict = {'+': 2, '-': 3}
        ValidOPDict = {"Max": 2}
        Operators = ['+', '-']
        expected = [True, False]
        result = MaskOPSpace(func_arity_dict, ValidOPDict, Operators)
        self.assertEqual(result, expected)

    def test_multiple_operators_all_invalid(self):
        func_arity_dict = {'+': 3, '-': 4}
        ValidOPDict = {"Max": 2}
        Operators = ['+', '-']
        expected = [False, False]
        result = MaskOPSpace(func_arity_dict, ValidOPDict, Operators)
        self.assertEqual(result, expected)

    def test_no_max_arity(self):
        func_arity_dict = {'+': 2, '-': 3}
        ValidOPDict = {"Max": None}
        Operators = ['+', '-']
        expected = [False, False]
        result = MaskOPSpace(func_arity_dict, ValidOPDict, Operators)
        self.assertEqual(result, expected)

class TestMaskActionSpace(unittest.TestCase):
    def test_empty_inputs(self):
        Constants = None
        Features = None
        DeltaTimes = None
        CSOperators = None
        TSOperators = None
        func_arity_dict = {}
        ValidDict = {
            "Constant": False,
            "Feature": False,
            "DeltaTime": False,
            "CSOperator": {"Max": None},
            "TSOperator": {"Max": None},
            "SEP": False
        }
        expected = [False]
        result = MaskActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators, func_arity_dict, ValidDict)
        self.assertEqual(result, expected)

    def test_constants_only(self):
        Constants = [1.0, 2.0]
        Features = None
        DeltaTimes = None
        CSOperators = None
        TSOperators = None
        func_arity_dict = {}
        ValidDict = {
            "Constant": True,
            "Feature": False,
            "DeltaTime": False,
            "CSOperator": {"Max": None},
            "TSOperator": {"Max": None},
            "SEP": False
        }
        expected = [True, True, False]

        result = MaskActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators, func_arity_dict, ValidDict)
        self.assertEqual(result, expected)

    def test_features_only(self):
        Constants = None
        Features = ["$feature1", "$feature2"]
        DeltaTimes = None
        CSOperators = None
        TSOperators = None
        func_arity_dict = {}
        ValidDict = {
            "Constant": False,
            "Feature": True,
            "DeltaTime": False,
            "CSOperator": {"Max": None},
            "TSOperator": {"Max": None},
            "SEP": False
        }
        expected = [True, True, False]
        result = MaskActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators, func_arity_dict, ValidDict)
        self.assertEqual(result, expected)

    def test_deltatimes_only(self):
        Constants = None
        Features = None
        DeltaTimes = [1, 2]
        CSOperators = None
        TSOperators = None
        func_arity_dict = {}
        ValidDict = {
            "Constant": False,
            "Feature": False,
            "DeltaTime": True,
            "CSOperator": {"Max": None},
            "TSOperator": {"Max": None},
            "SEP": False
        }
        expected = [True, True, False]
        result = MaskActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators, func_arity_dict, ValidDict)
        self.assertEqual(result, expected)

    def test_csoperators_only(self):
        Constants = None
        Features = None
        DeltaTimes = None
        CSOperators = ["+", "-"]
        TSOperators = None
        func_arity_dict = {'+': 2, '-': 2}
        ValidDict = {
            "Constant": False,
            "Feature": False,
            "DeltaTime": False,
            "CSOperator": {"Max": 2},
            "TSOperator": {"Max": None},
            "SEP": False
        }
        expected = [True, True, False]
        result = MaskActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators, func_arity_dict, ValidDict)
        self.assertEqual(result, expected)

    def test_tsoperators_only(self):
        Constants = None
        Features = None
        DeltaTimes = None
        CSOperators = None
        TSOperators = ["ref"]
        func_arity_dict = {'ref': 1}
        ValidDict = {
            "Constant": False,
            "Feature": False,
            "DeltaTime": False,
            "CSOperator": {"Max": None},
            "TSOperator": {"Max": 1},
            "SEP": False
        }
        expected = [True,False]
        result = MaskActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators, func_arity_dict, ValidDict)
        self.assertEqual(result, expected)

    def test_all_inputs(self):
        Constants = [1.0]
        Features = ["$feature1"]
        DeltaTimes = [1]
        CSOperators = ["+"]
        TSOperators = ["ref"]
        func_arity_dict = {'+': 2, 'ref': 1}
        ValidDict = {
            "Constant": True,
            "Feature": True,
            "DeltaTime": True,
            "CSOperator": {"Max": 2},
            "TSOperator": {"Max": 1},
            "SEP": True
        }
        expected = [
            True,
            True,
            True,
            True,
            True,
            True
        ]
        result = MaskActionSpace(Constants, Features, DeltaTimes, CSOperators, TSOperators, func_arity_dict, ValidDict)
        self.assertEqual(result, expected)



  

if __name__ == '__main__':
    # # unittest.main()
    # # only test the GetActionSpace function
    # suite = unittest.TestSuite()
    # suite.addTest(TestGetActionSpace('test_empty_inputs'))
    # suite.addTest(TestGetActionSpace('test_constants_only'))
    # suite.addTest(TestGetActionSpace('test_features_only'))
    # suite.addTest(TestGetActionSpace('test_deltatimes_only'))
    # suite.addTest(TestGetActionSpace('test_operators_only'))
    # suite.addTest(TestGetActionSpace('test_all_inputs'))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    # # only test the GetArityDict function
    # suite = unittest.TestSuite()
    # suite.addTest(TestGetArityDict('test_empty_ops'))
    # suite.addTest(TestGetArityDict('test_single_op'))
    # suite.addTest(TestGetArityDict('test_multiple_ops_same_arity'))
    # suite.addTest(TestGetArityDict('test_multiple_ops_different_arity'))
    # suite.addTest(TestGetArityDict('test_complex_ops'))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    # # only test the MaskOPSpace function
    # suite = unittest.TestSuite()
    # suite.addTest(TestGetActionSpace('test_empty_inputs'))
    # suite.addTest(TestGetActionSpace('test_constants_only'))
    # suite.addTest(TestGetActionSpace('test_features_only'))
    # suite.addTest(TestGetActionSpace('test_deltatimes_only'))
    # suite.addTest(TestGetActionSpace('test_operators_only'))
    # suite.addTest(TestGetActionSpace('test_all_inputs'))
    # suite.addTest(TestGetArityDict('test_empty_ops'))
    # suite.addTest(TestGetArityDict('test_single_op'))
    # suite.addTest(TestGetArityDict('test_multiple_ops_same_arity'))
    # suite.addTest(TestGetArityDict('test_multiple_ops_different_arity'))
    # suite.addTest(TestGetArityDict('test_complex_ops'))
    # suite.addTest(TestMaskOPSpace('test_empty_operators'))
    # suite.addTest(TestMaskOPSpace('test_single_operator_valid'))
    # suite.addTest(TestMaskOPSpace('test_single_operator_invalid'))
    # suite.addTest(TestMaskOPSpace('test_multiple_operators_all_valid'))
    # suite.addTest(TestMaskOPSpace('test_multiple_operators_some_invalid'))
    # suite.addTest(TestMaskOPSpace('test_multiple_operators_all_invalid'))
    # suite.addTest(TestMaskOPSpace('test_no_max_arity'))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    # only test the MaskActionSpace function
    suite = unittest.TestSuite()
    suite.addTest(TestMaskActionSpace('test_empty_inputs'))
    suite.addTest(TestMaskActionSpace('test_constants_only'))
    suite.addTest(TestMaskActionSpace('test_features_only'))
    suite.addTest(TestMaskActionSpace('test_deltatimes_only'))
    suite.addTest(TestMaskActionSpace('test_csoperators_only'))
    suite.addTest(TestMaskActionSpace('test_tsoperators_only'))
    suite.addTest(TestMaskActionSpace('test_all_inputs'))
    runner = unittest.TextTestRunner()
    runner.run(suite)