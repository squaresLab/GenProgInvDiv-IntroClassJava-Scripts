import xml.etree.ElementTree as ET
import sys
import glob

def get_xml_roots(dir):
    '''
    :param dir: the path to the directory containing XML files with reports on test case passage & failures
    :return: a list of XML roots of test case reports
    '''
    reports = glob.glob(dir + "/*.xml")
    xmlroots = [ET.parse(r).getroot() for r in reports]
    return xmlroots

def get_pos_neg_tests(xmlroot):
    '''
    :param xmlroot: the root of an XML file with reports on test case passage & failures
    :return: a tuple: (list of positive test cases, list of negative test cases)
    '''
    postests = list()
    negtests = list()
    if(xmlroot.tag != "testsuite"):
        print("Unexpected root of XML test case report: " + xmlroot.tag)
        print("Will continue to attempt to parse anyways")
    for testcase in xmlroot:
        if testcase.tag == "testcase":
            name = testcase.attrib["classname"] + "::" + testcase.attrib["name"]
            is_negative = False
            for failure in testcase:
                if failure.tag == "failure":
                    is_negative = True
                    break
            if is_negative:
                negtests.append(name)
            else:
                postests.append(name)
    return (postests, negtests)

def write_list_to_file(list, filename):
    with open(filename, mode="w") as outfile:
        for test in list:
            outfile.write(test + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: 1st argument: path to directory containing XML files with reports on test case passage & failures\n" +
              "\tProbably BUGDIR/target/surefire-reports/\n" +
              "2nd argument: path to create file containing list of positive tests\n" +
              "3rd argument: path to create file containing list of negative tests\n")
        exit(1)

    reports_dir = sys.argv[1]
    pos_file_path = sys.argv[2]
    neg_file_path = sys.argv[3]
    xml_roots = get_xml_roots(reports_dir)
    postests = list()
    negtests = list()
    pos_neg_lists = [get_pos_neg_tests(r) for r in xml_roots]
    for tup in pos_neg_lists:
        postests.extend(tup[0])
        negtests.extend(tup[1])

    write_list_to_file(postests, pos_file_path)
    write_list_to_file(negtests, neg_file_path)
