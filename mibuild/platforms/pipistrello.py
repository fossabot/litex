from mibuild.generic_platform import *
from mibuild.crg import SimpleCRG
from mibuild.xilinx.ise import XilinxISEPlatform
from mibuild.xilinx.programmer import XC3SProg

_io = [
	("user_led", 0, Pins("V16"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")), # green near hdmi
	("user_led", 1, Pins("U16"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")), # red near hdmi
	("user_led", 2, Pins("A16"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")), # green at msd
	("user_led", 3, Pins("A15"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")), # red at msd
	("user_led", 4, Pins("A12"), IOStandard("LVTTL"), Drive(8), Misc("SLEW=QUIETIO")), # red at usb

	("user_switch", 0, Pins("N14"), IOStandard("LVTTL"), Misc("PULLDOWN")),

	("clk50", 0, Pins("H17"), IOStandard("LVTTL")),

	("serial", 0,
		Subsignal("tx", Pins("A10"), Misc("SLEW=SLOW")),
		Subsignal("rx", Pins("A11"), Misc("PULLUP")),
		Subsignal("rts", Pins("C10"), Misc("SLEW=SLOW")),
		Subsignal("cts", Pins("A9"), Misc("PULLUP")),
		IOStandard("LVTTL"),
	),

	("usb_fifo", 0,
		Subsignal("data", Pins("A11 A10 C10 A9 B9 A8 B8 A7")),
		Subsignal("rxf", Pins("C7")),
		Subsignal("txe", Pins("A6")),
		Subsignal("rd", Pins("B6")),
		Subsignal("wr", Pins("A5")),
		Subsignal("siwua", Pins("C5")),
		IOStandard("LVTTL"),
	),

	("dvi_in", 0,
		Subsignal("clk_p", Pins("U5"), IOStandard("TMDS_33")),
		Subsignal("clk_n", Pins("V5"), IOStandard("TMDS_33")),
		Subsignal("data0_p", Pins("T6"), IOStandard("TMDS_33")),
		Subsignal("data0_n", Pins("V6"), IOStandard("TMDS_33")),
		Subsignal("data1_p", Pins("U7"), IOStandard("TMDS_33")),
		Subsignal("data1_n", Pins("V7"), IOStandard("TMDS_33")),
		Subsignal("data2_p", Pins("U8"), IOStandard("TMDS_33")),
		Subsignal("data2_n", Pins("V8"), IOStandard("TMDS_33")),
		Subsignal("scl", Pins("V9"), IOStandard("LVCMOS33")),
		Subsignal("sda", Pins("T9"), IOStandard("LVCMOS33")),
		Subsignal("hpd_notif", Pins("R8"), IOStandard("LVCMOS33")),
	),

	("spiflash", 0,
		Subsignal("cs_n", Pins("V3")),
		Subsignal("clk", Pins("R15")),
		Subsignal("mosi", Pins("T13")),
		Subsignal("miso", Pins("R13"), Misc("PULLUP")),
		Subsignal("wp", Pins("T14")),
		Subsignal("hold", Pins("V14")),
		IOStandard("LVTTL"), Misc("SLEW=FAST")
	),

	("spiflash2x", 0,
		Subsignal("cs_n", Pins("V3")),
		Subsignal("clk", Pins("R15")),
		Subsignal("dq", Pins("T13", "R13"), Misc("PULLUP")),
		Subsignal("wp", Pins("T14")),
		Subsignal("hold", Pins("V14")),
		IOStandard("LVCMOS33"), Misc("SLEW=FAST")
	),

	("mmc", 0,
		Subsignal("clk", Pins("A3")),
		Subsignal("cmd", Pins("B3")),
		Subsignal("dat", Pins("B4 A4 B2 A2")),
		IOStandard("SDIO")
	),

	("audio", 0,
		Subsignal("l", Pins("R7")),
		Subsignal("r", Pins("T7")),
		IOStandard("LVTTL"),
	),

	("pmod", 0,
		Subsignal("d", Pins("D9 C8 D6 C4 B11 C9 D8 C6")),
		IOStandard("LVCMOS33")
	),

	("sdram_clock", 0,
		Subsignal("p", Pins("G3")),
		Subsignal("n", Pins("G1")),
		IOStandard("MOBILE_DDR"), Misc("SLEW=FAST"),
	),

	("sdram", 0,
		Subsignal("a", Pins("J7 J6 H5 L7 F3 H4 H3 H6 D2 D1 F4 D3 G6")),
		Subsignal("ba", Pins("F2 F1")),
		# Subsignal("cs_n", Pins("")),
		Subsignal("cke", Pins("H7")),
		Subsignal("ras_n", Pins("L5")),
		Subsignal("cas_n", Pins("K5")),
		Subsignal("we_n", Pins("E3")),
		Subsignal("dq", Pins("L2 L1 K2 K1 H2 H1 J3 J1 M3 M1 N2 N1 T2 T1 U2 U1")),
		Subsignal("dm", Pins("K3 K4")),
		IOStandard("MOBILE_DDR"), Misc("SLEW=FAST")
	)
]

_connectors = [
	("A", "U18 T17 P17 P16 N16 N17 M16 L15 L17 K15 K17 J16 H15 H18 F18 D18"),
	("B", "C18 E18 G18 H16 J18 K18 K16 L18 L16 M18 N18 N15 P15 P18 T18 U17"),
	("C", "F17 F16 E16 G16 F15 G14 F14 H14 H13 J13 G13 H12 K14 K13 K12 L12"),
]

class Platform(XilinxISEPlatform):
	identifier = 0x5049
	default_clk_name = "clk50"
	default_clk_period = 20

	def __init__(self):
		XilinxISEPlatform.__init__(self, "xc6slx45-csg324-2", _io,
			lambda p: SimpleCRG(p, "clk50", None), _connectors)

	def create_programmer(self):
		return XC3SProg("ftdi", "bscan_spi_lx45_csg324.bit")

	def do_finalize(self, fragment):
		try:
			self.add_period_constraint(self.lookup_request("clk50"), 20.)
		except ConstraintError:
			pass
