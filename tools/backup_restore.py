#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab

import tarfile
import os
import argparse
class BackupAndRestore:
    def __init__(self):
        self.files = []
        self.workdir = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])
        self.workdir_len = len(self.workdir.split(os.path.sep))-1
        self.backupdirs = ['etc','items','scenes']
        self.exclude_files = ('.default','.gitignore')
        self.verbose=False
        self.overwrite=False

    def backup(self, outfile, include=None, exclude=None):
        if os.path.isfile(outfile) and self.overwrite == False:
            raise ValueError("Outputfile exists "+ outfile)
        if exclude != None:
            self.backupdirs = set(self.backupdirs) - set(exclude)
        if include != None:
            self.backupdirs = self.backupdirs+include
        if self.verbose: print (self.backupdirs)
        for path in self.backupdirs:
            self.get_files(os.path.join(self.workdir, path))
        if self.verbose: print (self.files)
        tar = tarfile.open(outfile, "w:gz")
        for name in self.files:
            tar.add(name, filter=self.change_fileinfo)
        tar.close()
         

    def get_files(self,apath):
        if not os.path.exists(apath):
            raise ValueError(" Directory not found! '" + apath + "'")

        for root, dirnames, filenames in os.walk(apath):
            for filename in filenames:
                if not filename.lower().endswith(self.exclude_files):
                    self.files.append(os.path.join(root, filename))

    def change_fileinfo(self,tarinfo):
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        newname = os.path.sep.join(tarinfo.name.split(os.path.sep)[self.workdir_len:])
        if self.verbose: print(newname)
        tarinfo.name = newname
        return tarinfo

    def restore(self, afile, outdir, selector=None):

        tar = tarfile.open(afile, "r:gz")
        tar.extractall(path=outdir)
        tar.close() 

if __name__ == '__main__':
    bar = BackupAndRestore()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--backup', action='store_true', help='create a config backup')
    group.add_argument('-r', '--restore',  action='store', help='restore a backup',metavar='dir')
    parser.add_argument('--backupfile', action='store', help='name for outputfile (default: backup.tar.gz)',metavar='dir', default='backup.tar.gz')
    parser.add_argument('--include', nargs='+', action='store', help='include directory to backup',metavar='dir')
    parser.add_argument('--exclude', nargs='+', action='store', help='exclude directory from backup (only for etc,items,scenes)',metavar='dir')
    parser.add_argument('-v','--verbose', action='store_true', help='generate more output', default=False)
    parser.add_argument('--overwrite', action='store_true', help='allways overwrite existing files', default=False)
    args = parser.parse_args()
    try:
        if args.verbose:
            print (args)
            bar.verbose=True
        if args.overwrite:
            bar.overwrite=True
        if args.backup:
            bar.backup(outfile=args.backupfile, include=args.include, exclude=args.exclude)
        if args.restore != None:
            bar.restore(afile=args.backupfile, outdir=args.restore)
    except ValueError as e:
        print("")
        print(e)
        print("")
        parser.print_help()
        exit(1)   
