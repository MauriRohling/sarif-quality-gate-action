import json
import sys
import os

def read_file(file_path: str) -> dict:
    try:
        if file_path:
            with open(file_path, "r") as file:
                return json.load(file)
        else:
            raise FileNotFoundError("File path is empty.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")

def write_github_output(output_name: str, output_value: str):
    output_file_path = os.getenv('GITHUB_OUTPUT')
    if output_file_path:
        with open(output_file_path, 'a') as file:
            file.write(f"{output_name}={output_value}\n")

def get_result_level(result: dict, tool: dict) -> str:
    """
    Get the result level for a given result and tool.

    Parameters:
    result (dict): The result object.
    tool (dict): The tool object.

    Returns:
    str: The result level. Possible values are "error", "warning", "note", or "none".
    """

    # Check the level at the result
    result_level = result.get("level", None)
    if result_level is not None:
        return result_level

    # Check the level at defaultConfiguration 
    tool_index = result.get("rule", {}).get("toolComponent", {}).get("index")
    rule_index = result["rule"]["index"]

    # Check driver.rules if toolComponent.index is not present, extensions.rules otherwise
    if tool_index is None:
        default_configuration = tool["driver"]["rules"][rule_index]["defaultConfiguration"]
    else:
        default_configuration = tool["extensions"][tool_index]["rules"][rule_index]["defaultConfiguration"]
    
    return default_configuration.get("level", "warning") if default_configuration.get("enabled", True) else "none"

def count_result_levels(sarif_data: dict) -> dict:
    """
    Count the number of each result level in the SARIF data.

    Parameters:
    sarif_data (dict): The SARIF data.

    Returns:
    dict: A dictionary containing the amount of each rule violation level.
    """
    tool = sarif_data["runs"][0]["tool"]
    results = sarif_data["runs"][0]["results"]
    level_counter = {'error': 0, 'warning': 0, 'note': 0, 'none': 0}

    for result in results:
        level = get_result_level(result, tool)
        level_counter[level] += 1

    return level_counter


if __name__ == "__main__":
    sarif_file_path = os.environ.get("SARIF_FILE_PATH")
    max_errors = os.environ.get("MAX_ERRORS")
    max_warnings = os.environ.get("MAX_WARNINGS")
    max_notes = os.environ.get("MAX_NOTES")
    
    level_counts = count_result_levels(read_file(sarif_file_path))
    
    quality_gate = {
        "max_errors": int(max_errors) if max_errors else sys.maxsize,
        "max_warnings": int(max_warnings) if max_warnings else sys.maxsize,
        "max_notes": int(max_notes) if max_notes else sys.maxsize
    }
    
    failed = level_counts["error"] > quality_gate["max_errors"] or \
             level_counts["warning"] > quality_gate["max_warnings"] or \
             level_counts["note"] > quality_gate["max_notes"]
    
    print("Rule Violations Found:")
    for level, count in level_counts.items():
        print(f"{level}: {count}")
    
    if failed:
        print("Quality gate failed")
        write_github_output("quality-gate-status", "FAILED")
        sys.exit(1)
    
    print("Quality gate passed")
    write_github_output("quality-gate-status", "PASSED")
    sys.exit(0)
