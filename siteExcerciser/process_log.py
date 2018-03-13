import gzip
import re
import os
import datetime

def addFiles(rootDir, regexFilter = None):
    filesToProcess = []
    for root, directories, files in os.walk(rootDir):
        for filename in files:
            m = None
            if regexFilter != None:
                m = re.match(regexFilter, filename)
                if not m:
                    continue
            fileData = {}
            try:
                fileData["folder"] = root
                fileData["path"] = os.path.join(root, filename)
                fName, fExt = os.path.splitext(filename)
                fileData["ext"] = fExt
                fileData["name"] = fName
                fileData["match"] = m

                # dates
                fileData["modified"] = datetime.datetime.fromtimestamp(os.path.getmtime(fileData["path"]))
            except:
                fileData['Error'] = 'Error processing file'
                
            filesToProcess.append(fileData)
            
    return filesToProcess  

def select_files(file_path):
    regex_filter = re.compile(".*\.gz")
    file_list = addFiles(file_path, regex_filter)
    return file_list

def process_file(file_data):
    if 'path' not in file_data:
        return file_data

    re_date = re.compile(b'^([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}) - DEBUG -')
    re_request = re.compile(b'response_time="(.*)" endpoint="(.*)" request="(.*)"')
    re_response = re.compile(b'response="(.*)"')
    re_uid = re.compile(b'uid="(.*)" request_uri="(.*)" referer="(.*)" host="(.*)" agent="(.*)"')
    #response_time="(.*)" endpoint="(.*)" request="(.*)" response="(.*)" 
    #uid="([\d]+)" request_uri="(.*)" referer="(.*)" host="(.*)" agent="(.*)"

    i = 0
    file_name = file_data['path']
    rows = []
    row = {}

    with gzip.open(file_name) as f:
        for line in f:
            i += 1
            m = re.match(re_date, line)
            print(m)
            if m:
                if row:
                    print(row)
                    rows.append(row)
                row = {}       
                row['date'] = m.group(1)
            
            m = re.match(re_request, line)
            print(m)
            if m:
                row['response_time'] = m.group(1)
                row['endpoint'] = m.group(2)

            m = re.match(re_uid, line)
            print(m)
            if m:
                row['uid'] = m.group(1)
                row['referer'] = m.group(3)
                row['host'] = m.group(4)
                row['agent'] = m.group(5)

    if row:
        rows.append(row)

    print(i)
    file_data['lines'] = len(rows)
    return file_data, rows

def main():
    file_path = r"C:\opt\S3Bucket"
    file_list = select_files(file_path)
    for a_file in file_list:
        a_file, rows = process_file(a_file)
        print('\t{} => {}'.format(a_file['lines'], a_file['path']))
        if rows:
            print(rows[0])
            print(rows[-1])
        break

if __name__ == "__main__":
    main()