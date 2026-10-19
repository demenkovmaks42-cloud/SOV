import sys
import re

class SovCompiler:
    def __init__(self, source_code):
        self.source = source_code

    def compile(self):
        # Построчный разбор кода Sov v0.3
        lines = [line.strip() for line in self.source.split('\n') if line.strip()]
        var_name = "result"
        val1, val2, op = 0, 0, '+'
        port_val, data_val = None, None

        for line in lines:
            line_lower = line.lower()
            if "let" in line_lower or "=" in line:
                parts = line.replace("let", "").strip().split("=")
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    expr = parts[1].strip().replace(";", "")

                    for op_symbol, op_words in [('+', ['+']), ('-', ['-']), ('*', ['*'])]:
                        for w in op_words:
                            if w in expr:
                                nums = expr.split(w)
                                if len(nums) == 2:
                                    val1 = int(nums[0].strip())
                                    val2 = int(nums[1].strip())
                                    op = op_symbol
                                    break
            elif "out" in line_lower:
                match = re.search(r'out\s+(\d+),\s*(\d+)', line_lower)
                if match:
                    port_str, data_str = match.groups()
                    port_val, data_val = int(port_str), int(data_str)

        if op == '+': calc_result = val1 + val2
        elif op == '-': calc_result = val1 - val2
        else: calc_result = val1 * val2

        machine_code = bytearray()
        machine_code.append(0xB8)
        machine_code.extend(val1.to_bytes(4, 'little', signed=False))

        if op == '+':
            machine_code.append(0x05)
            machine_code.extend(val2.to_bytes(4, 'little', signed=False))
        elif op == '-':
            machine_code.append(0x2D)
            machine_code.extend(val2.to_bytes(4, 'little', signed=False))
        elif op == '*':
            machine_code.extend([0x69, 0xC0])
            machine_code.extend(val2.to_bytes(4, 'little', signed=False))

        if port_val is not None:
            machine_code.extend([0x66, 0xBA])
            machine_code.extend(port_val.to_bytes(2, 'little', signed=False))
            machine_code.append(0xB0)
            machine_code.append(data_val & 0xFF)
            machine_code.append(0xEE)

        machine_code.append(0xC3)
        return machine_code, calc_result

def main():
    if len(sys.argv) < 2:
        print("Использование: python sov_compiler.py <файл.sov>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        source = f.read()

    compiler = SovCompiler(source)
    bin_code, res = compiler.compile()

    out_file = sys.argv[1].replace('.sov', '.bin')
    with open(out_file, 'wb') as f:
        f.write(bin_code)

    print(f"[Sov] Успешно скомпилировано в {out_file}. Результат в EAX: {res}")

if __name__ == '__main__':
    main()
