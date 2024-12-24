from datetime import datetime


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


def validate_refinance_form( max_loan,loan_amount,tenure,repayment_id, max_tenure, total_due, loan_status, is_refinance):
    """
    Validate the refinance form data submitted by the user.

    Args:
    - request: The HTTP request object containing the form data.
    - max_loan: The maximum allowable loan amount.
    - max_tenure: The maximum allowable tenure (months).
    - total_due: The total due amount of the loan.
    - loan_status: The current status of the loan.
    - is_refinance: Boolean indicating if the loan is eligible for refinancing.

    Returns:
    - A tuple (valid, message). 'valid' is a boolean indicating whether the form data is valid,
      and 'message' contains the validation message.
    """
    print('loan_amount',loan_amount)
    print( 'total_due',total_due )
    print('tenure',tenure)
    print('max_tenure',max_tenure)
    print('max_loan',max_loan)
    print('formatted_date',repayment_id)
    print('loan_status',loan_status)
    print('is_refinance',is_refinance)

    # Validate refinance eligibility
    if is_refinance == "False":

        return [False, "This loan is not eligible for refinancing."]

    # Check loan status (already refinanced)
    elif loan_status == "refinanced":
        return [False, "This loan has already been refinanced."]

    # Validate loan amount
    elif loan_amount > max_loan:
        return[ False, f"Loan amount cannot be more than {max_loan}."]
    
    elif loan_amount < total_due:
        return [False, f"Loan amount cannot be less than {total_due}."]

    # Validate tenure
    elif tenure > max_tenure:
        return [False, f"Tenure cannot be more than {max_tenure} months."]

    # Everything is valid
    return [True, f"Form data is valid. Repayment start date: {repayment_id}"]


def validate_restructure_form(tenure,max_tenure,loan_status):
    print('tenure',tenure)
    print('max_tenure',max_tenure)
    print('loan_status',loan_status)
    if tenure > max_tenure:
        return [False, f"Tenure cannot be more than {max_tenure} months."]
    elif loan_status == 'restructured':
        return [False, "This loan has already been restructured."]
    return [True, f"Form data is valid."]
