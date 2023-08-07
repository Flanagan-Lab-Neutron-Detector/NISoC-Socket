# taken from Glasgow Amaranth PLL generation: 

pll_f_in = 24e6
pll_f_out = 180e6
simple_feedback = True

if not 10e6 <= pll_f_in <= 133e6:
    print(f"ERROR: PLL: f_in ({pll_f_in/1e6:.3f} MHz) must be between 10 and 133 MHz")
    exit(1)

if not 16e6 <= pll_f_out <= 275e6:
    print(f"ERROR: PLL: f_out ({pll_f_out/1e6:.3f} MHz) must be between 16 and 275 MHz")
    exit(2)

# simple feedback: fout = f_vco * (2 ** -divq)
#                       = f_pfd * (divf + 1) * (2 ** -divq)
#                       = (pll_f_in / (divr + 1)) * (divf + 1) * (2 ** -divq)
#                       = pll_f_in * (2 ** -divq) * (divf + 1) / (divr + 1)

# The documentation in the iCE40 PLL Usage Guide incorrectly lists the
# maximum value of DIVF as 63, when it is only limited to 63 when using
# feedback modes other that SIMPLE.
if simple_feedback:
    divf_max = 128
else:
    divf_max = 64

variants = []
for divr in range(0, 16):
    f_pfd = pll_f_in / (divr + 1)
    if not 10e6 <= f_pfd <= 133e6:
        continue

    for divf in range(0, divf_max):
        if simple_feedback:
            f_vco = f_pfd * (divf + 1)
            if not 533e6 <= f_vco <= 1066e6:
                continue

            for divq in range(1, 7):
                f_out = f_vco * (2 ** -divq)
                variants.append((divr, divf, divq, f_pfd, f_out))

        else:
            for divq in range(1, 7):
                f_vco = f_pfd * (divf + 1) * (2 ** divq)
                if not 533e6 <= f_vco <= 1066e6:
                    continue

                f_out = f_vco * (2 ** -divq)
                variants.append((divr, divf, divq, f_pfd, f_out))

if not variants:
    print(f"ERROR: PLL: f_in ({pll_f_in/1e6:.3f} MHz) to f_out ({pll_f_out/1e6:.3f}) constraints not satisfiable")
    exit(3)

def f_out_diff(variant):
    *_, f_out = variant
    return abs(f_out - pll_f_out)
divr, divf, divq, f_pfd, f_out = min(variants, key=f_out_diff)

if f_pfd < 17:
    filter_range = 1
elif f_pfd < 26:
    filter_range = 2
elif f_pfd < 44:
    filter_range = 3
elif f_pfd < 66:
    filter_range = 4
elif f_pfd < 101:
    filter_range = 5
else:
    filter_range = 6

if simple_feedback:
    feedback_path = "SIMPLE"
else:
    feedback_path = "NON_SIMPLE"

ppm = abs(pll_f_out - f_out) / pll_f_out * 1e6

print(f"PLL: f_in={pll_f_in/1e6:.3f} f_out(req)={pll_f_out/1e6:.3f} f_out(act)={f_out/1e6:.3f} [MHz] ppm={ppm}")
print(f"iCE40 PLL: feedback_path={feedback_path} divr={divr} divf={divf} divq={divq} filter_range={filter_range}")

