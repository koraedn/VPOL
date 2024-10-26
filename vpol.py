#!/usr/bin/env python
import re
import json
import os
import sys
import subprocess
import requests
from colorama import init, Fore, Style
from scapy.all import IP, TCP, UDP, send, sr1

init(autoreset=True)

class VPOLException(Exception):
    def __init__(self, message):
        self.message = message

class TerminalUtils:
    @staticmethod
    def setTitle(title):
        if os.name == 'nt':
            os.system(f'title {title}')
        else:
            print(f"\033]0;{title}\a", end='')

class VPOLProcessor:
    def __init__(self):
        self.vars = {}
        self.shouldExecute = None
        self.lines = []
        self.functions = {}
        self.in_if_block = False
        self.if_condition_met = False

    def run(self, code):
        self.lines = code.split('\n')
        inMultilineComment = False
        isFunctionDefining = False
        currentFunctionName = None
        currentFunctionBody = []

        lineNum = 0
        while lineNum < len(self.lines):
            line = self.lines[lineNum].strip()
            lineNum += 1

            try:
                if inMultilineComment:
                    if line.strip().endswith("]]"):
                        inMultilineComment = False
                    continue
                if line.strip().startswith("#[["):
                    inMultilineComment = True
                    continue

                if line.startswith("${"):
                    currentFunctionName = line[2:].strip()
                    isFunctionDefining = True
                    currentFunctionBody = []
                    continue

                elif line.strip() == "}" and isFunctionDefining:
                    self.functions[currentFunctionName] = currentFunctionBody
                    isFunctionDefining = False
                    continue

                elif isFunctionDefining:
                    currentFunctionBody.append(line)
                    continue

                else:
                    self.processLine(line, lineNum)

            except VPOLException as e:
                print(f"{Fore.RED}VPOL Error on line {lineNum}: {e.message}{Style.RESET_ALL}")
                return

    def processLine(self, line, lineNum):
        if not line:
            return

        if line.startswith('if'):
            self.evaluateIf(line, lineNum)
            return
        elif line.startswith('elseif'):
            self.evaluateElseIf(line, lineNum)
            return
        elif line.startswith('else:'):
            self.evaluateElse()
            return

        if not self.in_if_block or (self.in_if_block and self.shouldExecute):
            if line.startswith('@'):
                self.assignVar(line, lineNum)
            elif line.startswith('terminal.print'):
                self.printContent(line, lineNum)
            elif line.startswith('terminal.set_title'):
                self.setTitle(line, lineNum)
            elif line.startswith('cls()'):
                os.system('cls' if os.name == 'nt' else 'clear')
            elif line.startswith('json.parse'):
                self.parseJson(line, lineNum)
            elif line.startswith('network.ping'):
                self.ping(line, lineNum)
            elif line.startswith('network.http_check'):
                self.checkHttp(line, lineNum)
            elif line.startswith('network.send_packet'):
                self.sendPacket(line, lineNum)
            elif line.startswith('~$'):
                self.callFunction(line, lineNum)
            elif line.startswith('terminal.input'):
                self.inputVariable(line, lineNum)

    def callFunction(self, line, lineNum):
        match = re.search(r'~\$(\w+)', line)
        if not match:
            raise VPOLException("Invalid function call")
        
        functionName = match.group(1)
        if functionName not in self.functions:
            raise VPOLException(f"Function '{functionName}' not defined")
        
        for functionLine in self.functions[functionName]:
            self.processLine(functionLine, lineNum)

    def evaluateIf(self, line, lineNum):
        match = re.search(r'if (.+):', line)
        if not match:
            raise VPOLException("Invalid if statement")
        
        condition = match.group(1).strip()
        self.in_if_block = True
        self.shouldExecute = self.evaluateCondition(condition, lineNum)
        self.if_condition_met = self.shouldExecute

    def evaluateElseIf(self, line, lineNum):
        if not self.in_if_block:
            raise VPOLException("elseif without if")
            
        match = re.search(r'elseif (.+):', line)
        if not match:
            raise VPOLException("Invalid elseif statement")
        
        if not self.if_condition_met:
            condition = match.group(1).strip()
            self.shouldExecute = self.evaluateCondition(condition, lineNum)
            if self.shouldExecute:
                self.if_condition_met = True
        else:
            self.shouldExecute = False

    def evaluateElse(self):
        if not self.in_if_block:
            raise VPOLException("else without if")
        
        self.shouldExecute = not self.if_condition_met

    def evaluateCondition(self, condition, lineNum):
        if "=" in condition:
            left, right = map(str.strip, condition.split("="))
            left_value = self.evaluate(left, lineNum)
            right_value = self.evaluate(right, lineNum)
            return str(left_value) == str(right_value)
        raise VPOLException("Invalid if statement: only '=' comparisons are supported.")

    def inputVariable(self, line, lineNum):
        match = re.search(r'terminal\.input\("(.*)"\)\s*([@]\w+)', line)
        if not match:
            raise VPOLException("Invalid input statement")

        prompt = match.group(1)
        varName = match.group(2)[1:]
        
        value = input(prompt)
        self.vars[varName] = value

    def assignVar(self, line, lineNum):
        if line.strip().endswith("{"):
            varName = line.split('=')[0].strip()[1:]
            self.vars[varName] = ""
            return
        
        try:
            varName, value = line.split('=', 1)
        except ValueError:
            raise VPOLException("Invalid variable assignment")
        
        varName = varName.strip()[1:]
        value = self.evaluate(value.strip(), lineNum)
        self.vars[varName] = value

    def printContent(self, line, lineNum):
        match = re.search(r'terminal\.print\((.*)\)', line)
        if not match:
            raise VPOLException("Invalid print statement")
        
        content = match.group(1)
        result = self.evaluate(content.strip(), lineNum)
        print(result)

    def setTitle(self, line, lineNum):
        match = re.search(r'terminal\.set_title\((.*)\)', line)
        if not match:
            raise VPOLException("Invalid set_title statement")
        
        title = match.group(1).strip().strip('"')
        TerminalUtils.setTitle(title)

    def parseJson(self, line, lineNum):
        match = re.search(r'json\.parse\((.*)\ )', line)
        if not match:
            raise VPOLException("Invalid JSON parse statement")
        
        content = match.group(1)
        content = self.evaluate(content.strip(), lineNum)
        try:
            parsedJson = json.loads(content)
            return json.dumps(parsedJson, indent=4)
        except json.JSONDecodeError:
            raise VPOLException("Invalid JSON format")

    def ping(self, line, lineNum):
        match = re.search(r'network\.ping\((.*)\)', line)
        if not match:
            raise VPOLException("Invalid ping statement")
        
        ipAddress = self.evaluate(match.group(1), lineNum)
        try:
            if os.name == 'nt':
                output = subprocess.run(['ping', '-n', '4', ipAddress], capture_output=True, text=True)
            else:
                output = subprocess.run(['ping', '-c', '4', ipAddress], capture_output=True, text=True)
            print(output.stdout)
        except subprocess.CalledProcessError:
            raise VPOLException(f"Failed to ping {ipAddress}")

    def checkHttp(self, line, lineNum):
        match = re.search(r'network\.http_check\((.*)\)', line)
        if not match:
            raise VPOLException("Invalid http_check statement")
        
        url = self.evaluate(match.group(1), lineNum)
        try:
            response = requests.get(url, timeout=5)
            print(f"Successfully connected to {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to connect to {url}. Error: {str(e)}")

    def sendPacket(self, line, lineNum):
        match = re.search(r'network\.send_packet\((.*?)\)', line)
        if not match:
            raise VPOLException("Invalid send_packet statement")
        
        args = [self.evaluate(arg.strip(), lineNum) for arg in match.group(1).split(',')]
        if len(args) != 4:
            raise VPOLException("send_packet requires 4 arguments: IP, port, protocol, size")
        
        ip, port, protocol, size = args
        port = int(port)
        size = int(size)

        if protocol.lower() not in ['tcp', 'udp']:
            raise VPOLException("Protocol must be either 'tcp' or 'udp'")

        try:
            if protocol.lower() == 'tcp':
                packet = IP(dst=ip)/TCP(dport=port)/('X' * size)
            else:
                packet = IP(dst=ip)/UDP(dport=port)/('X' * size)

            response = sr1(packet, verbose=0)
            if response:
                print(f"Packet sent successfully to {ip}:{port} using {protocol.upper()}. Response received.")
            else:
                print(f"Packet sent to {ip}:{port} using {protocol.upper()}, but no response received.")
        except Exception as e:
            print(f"Failed to send packet to {ip}:{port}. Error: {str(e)}")

    def evaluate(self, expr, lineNum):
        if '+' in expr:
            parts = re.split(r'(\+)', expr)
            result = ''
            for part in parts:
                if part.strip() == '+':
                    continue
                result += str(self.evaluate(part.strip(), lineNum))
            return result

        if expr.startswith('@'):
            varName = expr[1:]
            if varName in self.vars:
                return self.vars[varName]
            else:
                raise VPOLException(f"Variable '{varName}' not defined.")
        
        return expr.strip().strip('"')

def main():
    if len(sys.argv) != 2:
        print("Usage: python vpol.py <script.vpol>")
        sys.exit(1)

    script_file = sys.argv[1]
    
    with open(script_file, 'r') as f:
        code = f.read()

    processor = VPOLProcessor()
    processor.run(code)

if __name__ == "__main__":
    main()
