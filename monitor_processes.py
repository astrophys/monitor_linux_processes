#!/bin/env python3
# Author : Ali Snedden
# Date   : 04/23/24
# License: MIT
# Notes :
#   Only works on linux
#
# To Do :
#   When I'm clever, I'll use inheritance with Process and CpuProcess / GpuProcess
#
#
"""This code does stuff
"""
#import os
import sys
import time
import argparse
import subprocess


class Process:
    """Generic Process that is parent class of CpuProcess and GpuProcess"""
    def __init__(self, pid : int, percentcpu : float, percentmem : float,
                 localtime : str, timesecs : int, command : str):
        """Monitor user processes by using Python

        Args:

        Returns:

        Raises:
        """
        self.pid=pid
        self.percentcpu=percentcpu
        self.percentmem=percentmem
        self.localtime=localtime
        self.timesecs=timesecs
        self.command=command


class CpuProcess(Process):
    """Process from a user"""
    def __init__(self, pid : int, user : str, virt : str, res : str,
                 shr : str, state : str, percentcpu : float, percentmem : float,
                 localtime : str, timesecs : int, command : str):
        """Monitor user processes by using Python

        Args:

        Returns:

        Raises:
        """
        super().__init__(pid=pid, percentcpu=percentcpu, percentmem=percentmem,
                         localtime=localtime, timesecs=timesecs, command=command)
        self.user=user
        self.virt = -1
        self.res  = -1
        self.shr  = -1
        self.parse_mem(virt, 'virt')
        self.parse_mem(res, 'res')
        self.parse_mem(shr, 'shr')
        self.state=state


    def parse_mem(self, memstr : str, attr : str) :
        """Parse memory string from top, handle different units. Set attribute 'attr'

        Args:
            memstr : (str) string of memory taken from top

        Returns:
            N/A : sets self.attr = value

        Raises:
        """
        try :
            if 't' in memstr.lower():
                mem = memstr.lower().split('t')[0]
                mem = float(mem) * 1024
            if 'g' in memstr.lower():
                mem = memstr.lower().split('g')[0]
                mem = float(mem)
            elif 'm' in memstr.lower():
                mem = memstr.lower().split('m')[0]
                mem = float(mem) / 1024
            elif 'k' in memstr.lower():
                mem = memstr.lower().split('k')[0]
                mem = float(mem) / (1024**2)
            else :
                mem = float(memstr) / (1024**2)
        except AttributeError :
            if type(memstr) == float:
                mem = memstr
        self.__setattr__(attr, mem)


    def write(self, fout) -> None :
        """Write out data to a file

        Args:
            fout : (file) open file to write to

        Returns:
            Nothing

        Raises:
        """
        fout.write("{:<19} : {:<8.1f} : {:<9} {:<5} {:<13.6f} {:<13.6f} {:<13.6f} "
                   "{:<6.2f} {:<6.2f} {}\n".format(self.localtime, self.timesecs,
                                        self.pid, self.user, self.virt, self.res,
                                        self.shr, self.percentcpu, self.percentmem,
                                        self.command))
        fout.flush()


class GpuProcess(Process):
    """GPU Process"""
    def __init__(self, pid : int, gpu : int, sm : str, mem, command : str,
                 localtime : str, timesecs : int):
        """Monitor gpu processes

        Args:

        Returns:

        Raises:
        """
        if sm == '-':
            sm = 0
        if mem == '-':
            mem = 0
        super().__init__(pid=pid, percentcpu=float(sm), percentmem=float(mem),
                         localtime=localtime, timesecs=timesecs, command=command)
        self.gpu = gpu      # gpu index


    def write(self, fout) -> None :
        """Write out data to a file

        Args:
            fout : (file) open file to write to

        Returns:
            Nothing

        Raises:
        """
        fout.write("{:<19} : {:<8.1f} : {:<9} {:<6.2f} {:<6.2f} "
                   "{}\n".format(self.localtime, self.timesecs, self.pid,
                                 self.percentcpu, self.percentmem, self.command))
        fout.flush()


def total_cpu_process(procL : list) -> CpuProcess :
    """Take list of Process's, sum up their values and returns a 'total' Process

    Args:
        procL : (list) of Process's

    Returns:
        Process

    Raises:
    """
    virt= 0
    res = 0
    shr = 0
    percentcpu = 0
    percentmem = 0
    localtime = procL[0].localtime
    timesecs  = procL[0].timesecs
    for proc in procL:
        if proc.localtime != localtime or proc.timesecs != timesecs :
            raise ValueError("ERROR!! procL aren't all from the same localtime "
                             "or have the same timesecs")
        virt += proc.virt
        res  += proc.res
        shr  += proc.shr
        percentcpu += proc.percentcpu
        percentmem += proc.percentmem
    totproc = CpuProcess(pid = -1, user = proc.user, virt = virt, res = res,
                      shr = shr, state = "N/A", percentcpu = percentcpu,
                      percentmem = percentmem, localtime = proc.localtime,
                      timesecs = proc.timesecs, command = "TOTALPROC")
    return totproc


def total_gpu_process(procL : list) -> Process :
    """Take list of GpuProcess's, sum up their values and returns a 'total' Process

    Args:
        procL : (list) of Process's

    Returns:
        Process

    Raises:
    """
    percentcpu = 0
    percentmem = 0
    localtime = procL[0].localtime
    timesecs  = procL[0].timesecs
    for proc in procL:
        if proc.localtime != localtime or proc.timesecs != timesecs :
            raise ValueError("ERROR!! procL aren't all from the same localtime "
                             "or have the same timesecs")
        percentcpu += proc.percentcpu
        percentmem += proc.percentmem
    totproc = GpuProcess(pid = -1, gpu = -1, sm = percentcpu, mem = percentmem,
                         localtime = proc.localtime, timesecs = proc.timesecs,
                         command = "TOTALPROC")
    return totproc


def main():
    """Monitor user processes by using Python

    Args:

    Returns:

    Raises:
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--user', metavar='username', type=str,
                        help='Username')
    parser.add_argument('--delay', metavar='delay', type=int,
                        help='Delay in (integer) seconds between query')
    parser.add_argument('--outstem', metavar='output_path_stem', type=str,
                        help='Output path stem')
    parser.add_argument('--verbose', metavar='true_or_false', type=str, nargs='?',
                        help='Print out each top / nvidia-smi to stdout')
    args = parser.parse_args()
    if args.verbose == None :
        verbose = False
    elif args.verbose.lower() == 'false':
        verbose = False
    elif args.verbose.lower() == 'true':
        verbose = True
    else:
        raise ValueError("ERROR!!! Invalid verbose option")
    user = args.user
    delay = args.delay
    start = time.time()
    startlocal = time.localtime()
    cpuprocL = []
    gpuprocL = []
    print("{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(startlocal.tm_year,
          startlocal.tm_mon, startlocal.tm_mday, startlocal.tm_hour,
          startlocal.tm_min, startlocal.tm_sec))
    totcpufile = open("{}-total_cpu.txt".format(args.outstem), "w+")
    totcpufile.write("{:<19} : {:<8} : {:<9} {:<5} {:<13} {:<13} {:<13} {:<6} {:<6}"
                  "{}\n".format("Date", "time", "pid", "user", "virt_GiB", "res_GiB",
                                "shr_GiB", "%cpu", "%mem", "command"))
    allcpufile = open("{}-all_cpu.txt".format(args.outstem), "w+")
    allcpufile.write("{:<19} : {:<8} : {:<9} {:<5} {:<13} {:<13} {:<13} {:<6} {:<6}"
                  "{}\n".format("Date", "time", "pid", "user", "virt_GiB",
                                "res_GiB", "shr_GiB", "%cpu", "%mem", "command"))

    totgpufile = open("{}-total_gpu.txt".format(args.outstem), "w+")
    totgpufile.write("{:<19} : {:<8} : {:<9} {:<6} {:<6} "
                  "{}\n".format("Date", "time", "pid", "%cpu", "%mem", "command"))
    allgpufile = open("{}-all_gpu.txt".format(args.outstem), "w+")
    allgpufile.write("{:<19} : {:<8} : {:<9} {:<6} {:<6} "
                  "{}\n".format("Date", "time", "pid", "user", "%cpu", "%mem", "command"))

    while True:
        # Get time
        localtime = time.localtime()
        localtime = "{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(localtime.tm_year,
                    localtime.tm_mon, localtime.tm_mday, localtime.tm_hour,
                    localtime.tm_min, localtime.tm_sec)
        ###### CPU ######
        # Should be careful of string injection
        # https://stackoverflow.com/a/28756533/4021436
        string="top -b -u {} -n 1 | grep {}".format(user,user)
        top = subprocess.getoutput(string)
        if verbose == True:
            print(top)
        topL = top.split('\n')
        cpuprocsattimeL = []       # procs ONLY at this current time
        timesecs = time.time() - start
        for line in topL:
            line = line.split()
            cpuproc = CpuProcess(pid=int(line[0]), user=line[1], virt=line[4],
                                 res=line[5], shr=line[6], state=line[7],
                                 percentcpu=float(line[8]), percentmem=float(line[9]),
                                 localtime=localtime, timesecs=timesecs,
                                 command = line[-1])
            cpuproc.write(allcpufile)
            cpuprocL.append(cpuproc)
            cpuprocsattimeL.append(cpuproc)
        totcpuproc = total_cpu_process(cpuprocsattimeL)
        totcpuproc.write(totcpufile)

        # Assume monitor_process is last process standing
        if len(cpuprocsattimeL) == 1:
            break

        ###### GPU ######
        string="nvidia-smi pmon -c 1"
        nvsmi = subprocess.getoutput(string)
        if verbose == True:
            print(nvsmi)
        nvsmiL = nvsmi.split('\n')
        gpuprocsattimeL = []       # procs ONLY at this current time
        timesecs = time.time() - start
        for line in nvsmiL:
            # Skip headers
            if line[0] == "#":
                continue
            line = line.split()
            # empty gpu
            if line[-1] == '-':
                continue
            gpuproc = GpuProcess(gpu=int(line[0]), pid=int(line[1]), sm=line[3],
                              mem=line[4], localtime=localtime,
                              timesecs=timesecs, command = line[-1])
            gpuproc.write(allgpufile)
            gpuprocL.append(gpuproc)
            gpuprocsattimeL.append(gpuproc)
        if len(gpuprocsattimeL) > 0:
            totgpuproc = total_gpu_process(gpuprocsattimeL)
            totgpuproc.write(totgpufile)

        time.sleep(delay)

    totfile.close()
    sys.exit(0)



if __name__ == "__main__":
    main()
