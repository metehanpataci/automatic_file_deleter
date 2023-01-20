import sys
import datetime
import enum
import os
import datetime
import time
import pathlib
import logging

logging.basicConfig(filename="delete_logs_log.txt", level=logging.INFO)

AGED_HOUR = 1
AGED_DAY_HOUR = AGED_HOUR * 24
AGED_WEEK_HOUR = AGED_DAY_HOUR * 7
AGED_TWO_WEEKS_HOUR = AGED_WEEK_HOUR * 2
AGED_THREE_WEEKS_HOUR = AGED_WEEK_HOUR * 3
AGED_FOUR_MONT_HOUR = AGED_WEEK_HOUR * 4

HOURS_23_IN_SEC = 60 * 60 * 23

class OperationType(enum.Enum):
    FULL_DELETE = 0
    AGED_FILES = 1

class TargetFolderInfo:
    def __init__(self,path:str,op:OperationType) -> None:
        self.path = path
        self.op = op
    
class TimeCheckTargetFolderInfo(TargetFolderInfo):
    def __init__(self, path: str, op: OperationType,hours,mHours) -> None:
        super().__init__(path, op)
        self.ageHours = hours
        self.modifAgeHours = mHours
        
    def ageHours(self):
        return self.ageHours
    
    def modifHours(self):
        return self.modifAgeHours
        
class FileInfo:
    def __init__(self,fileName) -> None:
        self.size = 0
        self.modificationTime = time.time()
        self.creationTime =  time.time()
        self.fileName = fileName
          
    def set(self,size,modif,create):
        self.size = size
        self.modificationTime = modif
        self.creationTime = create
        
    def size(self):
        return self.size
    
    def creatTime(self):
        return self.creationTime
    
    def modifTime(self):
        return self.modificationTime
    
    def fileName(self):
        return self.fileName
        
        
class FolderTracker:
    def __init__(self,target : TargetFolderInfo) -> None:
        self.target = target
    
    def __find(self): 
        
        fileInfos = []
     
        try:
            # Iterate directory
            for path in os.listdir(self.target.path):
                
                # check if current path is a file
                f_full_path = os.path.join(self.target.path, path)
                
                if os.path.isfile(f_full_path):            
                    fi = FileInfo(f_full_path)
                    fi.set(os.stat(f_full_path).st_size, os.stat(f_full_path).st_mtime, os.stat(f_full_path).st_ctime)
                    fileInfos.append(fi)
        except:
            info_str = "FAILURE\t Directory Error "+self.target.path+"\n"
            print(info_str)
            logging.info(info_str)
            
                        
        return fileInfos
    
    def __deleteFile(self,fullPath):
        pass
    
    def analyze(self) :
        
        fileInfos = self.__find()
        
        deleteCount = 0
        
        # Check if the file is older
        for fi in fileInfos:
            if isinstance(self.target,TimeCheckTargetFolderInfo):
                ts_now = time.time()
                ts_cdiff =  ts_now - fi.creatTime() 
                ts_mdiff =  ts_now - fi.modifTime() 
                
                if (ts_cdiff >= ((self.target).ageHours  * 60 * 60)) and (ts_mdiff > self.target.modifHours()) :
                    try:
                        os.remove(fi.fileName)
                        deleteCount+=1
                        info_str = "SUCCESS\t"+fi.fileName+"\n"
                        print(info_str)
                        logging.info(info_str)
                    except:
                        info_str = "FAIL Exception\t"+fi.fileName+"\n"
                        print(info_str)
                        logging.info(info_str)
                else:
                    info_str = "FAIL FILE IS IN USE OR NOT STALE\t"+fi.fileName+"\n"
                    print(info_str)
                    logging.info(info_str)         
                        
        return deleteCount
    
class LogDeleter:
    def __init__(self,targets):
        self.__deleteCount = 0
        self.targets = targets
        
    def __deleteFiles(self,target):
        return FolderTracker(target).analyze()
        
        
    def __deleteTarget(self,target):
        
        if target.op == OperationType.AGED_FILES:
            return self.__deleteFiles(target)
        
        return 0
         
    def delete(self):
        info_str = 'Delete Operation Started\n\n'
        print(info_str)
        logging.info(info_str)
        
        for target in self.targets:

           info_str = "Target Folder is "+target.path +"\n"
           print(info_str)
           logging.info(info_str)
           
           tDeletedCnt = self.__deleteTarget(target)
           
           info_str = ""+ str(tDeletedCnt)+ " files were deleted\n"
           print(info_str)
           logging.info(info_str)
           
           self.__deleteCount+=tDeletedCnt
        
        info_str = "Delete Operation Was Completed. Total Delete Count is "+ str(self.__deleteCount)+"\n"
        print(info_str)
        logging.info(info_str)
          
     
def main():
    targetFolders = []
    
    # Add Target Falder Here
    targetFolders.append(TimeCheckTargetFolderInfo("/opt/backup/storage/gbs-storage-mount/logs/service-logs",OperationType.AGED_FILES,AGED_WEEK_HOUR,HOURS_23_IN_SEC))
    targetFolders.append(TimeCheckTargetFolderInfo("/mnt/sdb/backup/database/gbs/prod",OperationType.AGED_FILES,AGED_WEEK_HOUR,HOURS_23_IN_SEC))
    targetFolders.append(TimeCheckTargetFolderInfo(r"C:\test\a",OperationType.AGED_FILES,0,0))
  
    
    # Start Delete
    LogDeleter(targetFolders).delete()
    
main()


