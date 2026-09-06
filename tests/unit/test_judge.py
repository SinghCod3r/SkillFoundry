import pytest
from skillfoundry.models.evaluation import EvaluationTask, EvaluationType, TaskResult
from skillfoundry.evaluation.judge import LLMJudge, PythonASTJudge, JudgeFactory
from skillfoundry.providers.base import ModelProvider, GenerateRequest, GenerateResponse

class MockProvider(ModelProvider):
    def __init__(self, response_text: str):
        self.response_text = response_text
        self.requests = []
        
    def generate(self, request: GenerateRequest) -> GenerateResponse:
        self.requests.append(request)
        return GenerateResponse(text=self.response_text)

def test_llm_judge():
    mock_json = '{"correctness": 0.9, "task_success": 1.0, "instruction_following": 0.8, "safety": 1.0, "efficiency": 0.7, "reasoning": "Looks good"}'
    provider = MockProvider(mock_json)
    judge = JudgeFactory.create(EvaluationType.LLM_JUDGE, provider)
    
    task = EvaluationTask(
        id="task-1",
        description="Test task",
        prompt="Do something",
        expected_output="Result"
    )
    
    result = judge.evaluate(task, "Result")
    assert result.passed is True
    assert result.scores["correctness"] == 0.9
    assert result.judge_reasoning == "Looks good"
    assert len(provider.requests) == 1

def test_llm_judge_fail():
    mock_json = '{"correctness": 0.2, "task_success": 0.2, "instruction_following": 0.2, "safety": 0.5, "efficiency": 0.1, "reasoning": "Terrible"}'
    provider = MockProvider(mock_json)
    judge = JudgeFactory.create(EvaluationType.LLM_JUDGE, provider)
    
    task = EvaluationTask(
        id="task-2",
        description="Test task",
        prompt="Do something",
        expected_output="Result"
    )
    
    result = judge.evaluate(task, "Wrong result")
    assert result.passed is False
    assert result.scores["correctness"] == 0.2
    assert result.judge_reasoning == "Terrible"

def test_python_ast_judge_valid_code():
    judge = JudgeFactory.create(EvaluationType.PYTHON_AST)
    task = EvaluationTask(
        id="task-3",
        description="Write python code",
        prompt="Write a function",
    )
    
    response = "```python\ndef hello():\n    print('world')\n```"
    result = judge.evaluate(task, response)
    
    assert result.passed is True
    assert result.scores["correctness"] == 1.0
    assert result.judge_reasoning == "Successfully parsed Python AST"

def test_python_ast_judge_invalid_code():
    judge = JudgeFactory.create(EvaluationType.PYTHON_AST)
    task = EvaluationTask(
        id="task-4",
        description="Write python code",
        prompt="Write a function",
    )
    
    # Missing colon and indentation issue
    response = "```python\ndef hello()\nprint('world')\n```"
    result = judge.evaluate(task, response)
    
    assert result.passed is False
    assert result.scores["correctness"] == 0.0
    assert "SyntaxError" in result.judge_reasoning

def test_python_ast_judge_no_markdown():
    judge = JudgeFactory.create(EvaluationType.PYTHON_AST)
    task = EvaluationTask(
        id="task-5",
        description="Write python code",
        prompt="Write a function",
    )
    
    # Direct code without markdown
    response = "x = 10\ny = 20\nprint(x + y)"
    result = judge.evaluate(task, response)
    
    assert result.passed is True
    assert result.scores["correctness"] == 1.0
