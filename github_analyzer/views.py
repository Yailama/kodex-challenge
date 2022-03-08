from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
import requests
import re

# Create your views here.



def index(request):
    return render(request, "github_analyzer/index.html")


def repo_analysis(request):

    repo_url = request.GET['repo_url']
    test = count_layers_repo(repo_url)
    if test is None:
        return HttpResponseBadRequest()
    else:
        risk_classification(test)
        return JsonResponse(test)


def clean_from_spaces(content: str):
    subs = {",\s{0,}\n{1,}": ", ",
            "\n{1,}\s{0,},\s{0,}": ", ",
            "\.\s{0,}\n{1,}": ". ",
            "\{\s{0,}\n{1,}": "{ ",
            "\[\s{0,}\n{1,}": "[ ",
            "\\\s{0,}\n{1,}": " ",
            "=\s{0,}\n{1,}": "= ",
            "\n{1,}=\s{0,}": "= ",
            "\n{1,}\s{0,}\(": " ("
            }
    for key, val in subs.items():
        content = re.sub(key, val, content)
    return content


def clean_from_comment(content: str):
    output = {}
    count = 0
    comment_block = False
    comment_block_start = ("'''")
    for line in content.split("\n"):
        line_strip = line.strip()
        count += 1
        if line_strip[:3] == comment_block_start:
            comment_block = 1 - comment_block

        if not comment_block:
            if line_strip.startswith('"""') or line_strip.startswith("'''"):
                if line_strip[:3] != line_strip[-3:]:
                    comment_block = True
                    comment_block_start = line_strip[:3]
            else:
                # if not line comment:
                if not (line_strip.startswith('#')):
                    line = re.sub("#.*", "", line)
                    output[count] = line
    return output


def clean_content(content: str):
    content = clean_from_spaces(content)
    content = clean_from_comment(content)
    return content


def count_layers_file(file):
    models = {}
    for rowline, line in file.items():

        if re.match(".*=\s{0,1}.*Sequential\(.*", line):
            model = re.sub("=\s{0,1}.*Sequential\s{0,}\(.*", "", line).strip()
            models[model] = {"total": 0, "relu": {"count": 0, "lines": []},
                             "sigmoid": {"count": 0, "lines": []}}
        if re.match(".*\.add\(\s{0,}Dense\s{0,}\(\s{0,}.*activation\s{0,}=\s{0,}'.*'\s{0,}\)", line):
            model, layer = (re.sub("\.add.*", "", line).strip(),
                            re.sub("'.*", "", re.sub(".*activation\s{0,}=\s{0,}'", "", line)).strip())
            models[model][layer]["count"] = models[model][layer]["count"] + 1
            models[model][layer]["lines"].append(rowline)
            models[model]["total"] = models[model]["total"] + 1

    return models


def count_layers_repo(repo_url):
    repo = re.sub(".*com/", "", repo_url)
    branch = "master"
    request_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=10"
    result = requests.get(request_url)
    if result.status_code == 404:
        branch = "main"
        request_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=10"
        result = requests.get(request_url)
    if result.status_code == 200:
        file_list = result.json()
        py_list = [x['path'] for x in file_list['tree'] if x['path'].endswith(".py")]
        output = {}
        for filename in py_list:
            file = requests.get(f"https://raw.githubusercontent.com/{repo}/{branch}/{filename}") \
                .content.decode("utf-8")
            output[filename] = count_layers_file(clean_content(file))
        return output
    else:
        return None


def risk_classification(models):
    #     The models should be classified as follows:
    # * 1-9 hidden layers: Low transparency risk
    # * 10-19 hidden layers: Medium transparency risk
    # * 20+ hidden layers: High transparency risk
    for file, model_dict in models.items():
        for key in model_dict.keys():
            hidden_layers = models[file][key]['total']
            if hidden_layers <= 9:
                models[file][key]['risk'] = "low"
            elif hidden_layers <= 19:
                models[file][key]['risk'] = "medium"
            else:
                models[file][key]['risk'] = "high"


