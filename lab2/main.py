from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as bf
from fake_useragent import UserAgent
import re
import pandas as pd
from tqdm import tqdm


def courseUrl(url: str) -> str:
    """get course list page suffix from given page

    Args:
        url (str): given url

    Returns:
        str: course list page
    """

    headers = {'User-Agent': UserAgent().random}
    ret = Request(url, headers=headers)
    res = urlopen(ret)
    data = res.read().decode('utf-8')
    soup = bf(data, features="lxml")

    suffix = soup.find('a', string=re.compile('.*?课程。*?'))['href']
    return url + suffix


def getCoursesID(url: str) -> tuple[list, list]:
    """get courses' links and courses' names

    Args:
        url (str): courses list page

    Returns:
        tuple[list, list]: courses' links and names
    """

    headers = {'User-Agent': UserAgent().random}
    ret = Request(url, headers=headers)
    res = urlopen(ret)
    data = res.read().decode('utf-8')
    soup = bf(data, features="lxml")

    links = soup.find_all(class_="px16")
    courses = []

    for index, link in enumerate(links):
        courses.append(link.text)
        links[index] = link['href']

    return links, courses


def courseInfo(courseID: str, courseName: str, serial: int) -> list:
    """get courses info

    Args:
        courseID (str): the courses id to course page
        courseName (str): course's name and teacher
        serial (int): serial of course

    Returns:
        info(list): info of the course
    """

    url = URL+courseID

    headers = {'User-Agent': UserAgent().random}
    ret = Request(url, headers=headers)
    res = urlopen(ret)
    data = res.read().decode('utf-8')
    soup = bf(data, features="lxml")

    info = []
    info.append(str(serial))
    info.append(courseName)

    block1 = soup.find_all(class_="right-mg-md", limit=5)
    del (block1[0])
    for name in block1:
        info.append(name.string.split('：')[-1])

    links = soup.find_all('strong', limit=6)

    for link in links:
        info.append(link.nextSibling)

    return info


URL = 'https://icourse.club'

url = courseUrl(URL)

result = []
counter = 0

for i in tqdm(range(1, 1484)):

    # get courses' link in one page
    links, names = getCoursesID(f'{url}?page={i}')

    # get course info
    for index, link in enumerate(links):
        result.append(courseInfo(link, names[index], counter))
        counter += 1
    # print(f"page{i} done!")

# print(result)
courseHeader = ['序号', '课程名称', '课程难度', '作业多少', '给分好坏',
                '收获大小', '选课类别', '教学类型', '课程类别', '开课单位', '课程层次', '学分']

result = pd.DataFrame(columns=courseHeader, data=result)
result.to_csv('courses.csv', index=False)
# result.to_json('courses.json', orient='records', force_ascii=False, indent=4)
