import gzip
import re
import os
import datetime
import csv

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
    re_request = re.compile(r' response_time="(.*)" endpoint="(.*)" request="(.*)"')
    re_response = re.compile(r' response="(.*)"')
    re_uid = re.compile(b'.* uid="([0-9]+)"')
    re_misc=re.compile(r' request_uri="(.*)" referer="(.*)" host="(.*)"')
    re_agent=re.compile(b'.* agent="(.*)"')
    #response_time="(.*)" endpoint="(.*)" request="(.*)" response="(.*)" 
    #uid="([\d]+)" request_uri="(.*)" referer="(.*)" host="(.*)" agent="(.*)"

    i = 0
    idx = 0
    file_name = file_data['path']
    rows = []
    row = {}

    with gzip.open(file_name, 'r') as f:
        for line in f:
            i += 1

            m = re.match(re_date, line)
            if m:
                if row:
                    rows.append(row)

                row = {}
                idx += 1
                row['idx'] = idx
                row['line'] = i
                row['date'] = m.group(1)

            mu = re.match(re_uid, line)
            if mu:
                row['uid'] = mu.group(1)

            ma = re.match(re_agent, line)
            if ma:
                row['agent'] = ma.group(1)

        if row:
            rows.append(row)
    
    file_data['lines'] = len(rows)
      
    return file_data, rows

def save_rows(file_name, rows):
    f_path = '{}.csv'.format(file_name)
    keys = ['uid', 'agent', 'date', 'idx', 'line']

    with open(f_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, keys)    
        writer.writeheader()
        writer.writerows(rows)

def main():
    file_path = r"C:\opt\S3Bucket"
    file_list = select_files(file_path)
    for a_file in file_list:
        a_file, rows = process_file(a_file)
        save_rows(a_file['name'], rows)

if __name__ == "__main__":
    main()