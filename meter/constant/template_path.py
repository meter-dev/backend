from meter.constant import ExtendedEnum

FOLDER = "./meter/template"


class TemplatePath(ExtendedEnum):
    ISSUE_TITLE = f"{FOLDER}/automated_generate_issue_title.template"
    ISSUE_CONTENT = f"{FOLDER}/automated_generate_issue_content.template"
