def tag_replacement(template: str, values: list[dict]) -> str:
    """
    Replaces placeholders in the template with corresponding values.
    
    :param template: The string containing placeholders.
    :param values: A list of dictionaries with 'name' and 'value' keys.
    :return: A string with placeholders replaced by their corresponding values.
    """
    print('Original template:', template)
    
    # Iterate over the list of replacements
    for data in values:
        name = data.get('name')  # Extract the placeholder name
        value = data.get('value')  # Extract the replacement value
        placeholder = f"{{{{{name}}}}}"  # Create the placeholder format (e.g., {{name}})
        
        print(f'Replacing placeholder: {placeholder} with value: {value}')
        template = template.replace(placeholder, value)  # Replace in the template
    
    return template