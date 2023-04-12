import sys


class Symbol_Tables:
    def __init__(self):
        self._reg_ref = self.extract_reg_ref("Symbole_Tables/register_reference_table.txt")
        self._io_ref = self.extract_io_ref("Symbole_Tables/input_output_table.txt")

    def extract_reg_ref(self, file):
        try:
            return open(file)
        except IOError:
            print("오류 발생")

    def extract_io_ref(self, file):
        try:
            return open(file)
        except IOError:
            print("오류 발생")

    def get_reg_ref_table(self):
        table = {}
        read = self._reg_ref.readline().split()
        while len(read) > 0: 
            table[read[0]] = read[1]
            read = self._reg_ref.readline().split()
        return table

    def get_io_ref_table(self):
        table = {}
        read = self._io_ref.readline().split()
        while len(read) > 0:
            table[read[0]] = read[1]
            read = self._io_ref.readline().split()
        return table
    
class Two_Pass_Assembler:
    def write_output(self):
        result = self.assemble()
        self.output_file = str(sys.argv[2])
        fil = open(self.output_file, 'w')
        for i in range(len(result)):
            fil.write(result[i].split()[0] + " "+ bin(int(result[i].split()[1], 16)).split("b")[1].zfill(16) + "\n")
        fil.close() 

    def complement_to_hex(self,num):
        binary = bin(int(num)).split("b")[1].zfill(16)
        binary = binary.replace("0", "x")
        binary = binary.replace("1", "0")
        binary = binary.replace("x", "1")
        return hex(int(binary, 2) + 1).split("x")[1]

    def __init__(self):
        self.dict = {}
        t = Symbol_Tables()
        self.reg_ref_table = t.get_reg_ref_table()
        self.io_ref_table = t.get_io_ref_table()
        self.mri_table = "and add lda sta bun bsa isz".split()
        self.labels = {}
        self.output = []
        self.output_dict = {}
    def first_pass(self):
        Loc_counter = 0
        line_Number = 1
        read = self.file.readline()
        while read != "":
            r = read.split(",")
            if len(r) > 1:
                if ("org" in r[1].lower()):
                    try:
                        Loc_counter = int(r[1].split()[1],16) - 1
                        if (Loc_counter+1 >= 4096):
                            self.output_dict["Error"]= str(line_Number) + "라인 오류"
                    except IndexError:
                        self.output_dict["Error"] = str(line_Number) + "라인 오류"
                else:
                    self.labels[r[0]] = hex(Loc_counter).split("x")[1].zfill(3)
                    
            else:
                if ("org" in r[0].lower()):
                    try:
                        Loc_counter = int(r[0].split()[1],16) - 1
                        if (Loc_counter+1 >= 4096):
                            self.output_dict["Error"] = str(line_Number) + "라인 오류"
                    except:
                        self.output_dict["Error"] = str(line_Number) + "라인 오류"     
            Loc_counter += 1
            line_Number += 1
            read = self.file.readline()
            if ("END" in read or read == ""):
                self.file.seek(0)
                break
    def second_pass(self):
        self.Loc_counter = 0
        line_Number = 1
        read = self.file.readline()
        while read != "":
            r = read.split(",")
            if len(r) > 1:
                if r[1].split()[0].lower() in {"org","dec","hex","end"}:
                    self.pseudo_helper(r[1].split(), line_Number)
                else:
                    self.output.append(str(self.Loc_counter).zfill(3) + " " + str(self.parse(r[1].split(), line_Number)))
            else:
                re = read.split()
                instruction = ""
                if len(re) == 0 or "end" in re[0].lower():
                    break
                elif re[0].lower() in ["org", "dec", "hex", "end"]:
                    self.pseudo_helper(re, line_Number)
                else:
                    self.output.append(str(self.Loc_counter).zfill(3) + " " + str(self.parse(re, line_Number)))
            self.Loc_counter += 1
            line_Number += 1
            read = self.file.readline()
        
    def pseudo_helper(self, ins_list, line):
        if "org" in ins_list[0].lower():
            try:
                self.Loc_counter = int(ins_list[1], 16) - 1
            except:
                self.output_dict["Error"] = str(line) + "라인 오류"
        elif "end" in ins_list[0].lower():
            sys.exit()
        elif "dec" in ins_list[0].lower():
            st = hex(int(ins_list[1])).split("x")
            if ("-" in ins_list[1]):
                st[1] = self.complement_to_hex(ins_list[1])
            else:
                st[1] = st[1].zfill(4)
            self.output.append(str(self.Loc_counter).zfill(3) + " " + str(st[1]))
        elif "hex" in ins_list[0].lower():
            self.output.append(str(self.Loc_counter).zfill(3) + " " + str(ins_list[1].zfill(4)))
            
    def parse(self, ins_list, line):
        instruction = ""
        if ins_list[0].lower() in self.mri_table:
            instruction += self.mri_helper(ins_list)
            try:
                if ins_list[1].isdigit():
                    instruction += ins_list[1]
                else:
                    instruction += str(self.labels[ins_list[1]])
            except:
                print("예외 발생")
                self.output_dict["Error"] = "라인 오류 발생"

        elif ins_list[0].lower() in self.reg_ref_table:
            if len(ins_list) > 1 and "/" not in ins_list[1]:
                print("라인 에러 : ", line)
                self.output_dict["Error"] = "라인 에러 : " + str(line)
                return
            instruction = self.reg_ref_table[ins_list[0].lower()]

        elif ins_list[0].lower() in self.io_ref_table:
            instruction = self.io_ref_table[ins_list[0].lower()]
        else:
            print("오류 발생")
            self.output_dict["Error"] = "라인 오류 발생"


        return instruction
    
    def mri_helper(self, ins_list):
        if ins_list[0].lower() == "and":
            return "8" if len(ins_list) > 2 and ins_list[2].lower() == "i" else "0"
        elif ins_list[0].lower() == "add":
            return "9" if len(ins_list) > 2 and ins_list[2].lower() == "i" else "1"
        elif ins_list[0].lower() == "lda":
            return "A" if len(ins_list) > 2 and ins_list[2].lower() == "i" else "2"
        elif ins_list[0].lower() == "sta":
            return "B" if len(ins_list) > 2 and ins_list[2].lower() == "i" else "3"
        elif ins_list[0].lower() == "bun":
            return "C" if len(ins_list) > 2 and ins_list[2].lower() == "i" else "4"
        elif ins_list[0].lower() == "bsa":
            return "D" if len(ins_list) > 2 and ins_list[2].lower() == "i" else "5"
        elif ins_list[0].lower() == "isz":
            return "E" if len(ins_list) > 2 and ins_list[2].lower() == "i" else "6"


    def assemble(self):
        input_file = str(sys.argv[1])
        self.file = open(input_file, "r")
        self.first_pass()
        self.second_pass()
        try:
            self.output_dict["Error"]
        except KeyError:
            self.output_dict = self.output
        return self.output_dict
    def read_output(self):
        sample = open(self.output_file, "r")
        fil = sample.readline()
        while(fil != ''):
            print(fil)
            fil = sample.readline()

            
def main():
    tpa = Two_Pass_Assembler()
    tpa.write_output()
    tpa.read_output()
       
main()
