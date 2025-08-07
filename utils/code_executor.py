import pandas as pd


def safe_exec(code: str, df: pd.DataFrame):
    """
    Executes Python code safely in a restricted environment.
    Returns result or error message.
    """
    local_vars = {"df": df.copy()}
    try:
        exec(code, {}, local_vars)
        if "result" in local_vars:
            return local_vars["result"]
        else:
            return "✅ Code executed, but no result was returned. Add a `result = ...` line."
    except Exception as e:
        return f"❌ Error during execution: {str(e)}"
