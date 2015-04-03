# This file is Copyright (c) 2014 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import os, subprocess, sys

from migen.fhdl.std import *
from migen.fhdl.structure import _Fragment
from mibuild.generic_platform import *

from mibuild import tools
from mibuild.xilinx import common

def _format_constraint(c):
	if isinstance(c, Pins):
		return "set_property LOC " + c.identifiers[0]
	elif isinstance(c, IOStandard):
		return "set_property IOSTANDARD " + c.name
	elif isinstance(c, Drive):
		return "set_property DRIVE " + str(c.strength)
	elif isinstance(c, Misc):
		return "set_property " + c.misc.replace("=", " ")
	else:
		raise ValueError("unknown constraint %s" % c)

def _format_xdc(signame, resname, *constraints):
	fmt_c = [_format_constraint(c) for c in constraints]
	fmt_r = resname[0] + ":" + str(resname[1])
	if resname[2] is not None:
		fmt_r += "." + resname[2]
	r = " ## %s\n" %fmt_r
	for c in fmt_c:
		r += c + " [get_ports " + signame + "]\n"
	return r

def _build_xdc(named_sc, named_pc):
	r = ""
	for sig, pins, others, resname in named_sc:
		if len(pins) > 1:
			for i, p in enumerate(pins):
				r += _format_xdc(sig + "[" + str(i) + "]", resname, Pins(p), *others)
		elif pins:
			r += _format_xdc(sig, resname, Pins(pins[0]), *others)
		else:
			r += _format_xdc(sig, resname, *others)
	if named_pc:
		r += "\n" + "\n\n".join(named_pc)
	return r

def _run_vivado(build_name, vivado_path, source, ver=None):
	if sys.platform == "win32" or sys.platform == "cygwin":
		build_script_contents = "REM Autogenerated by mibuild\n"
		build_script_contents += "vivado -mode batch -source " + build_name + ".tcl\n"
		build_script_file = "build_" + build_name + ".bat"
		tools.write_to_file(build_script_file, build_script_contents)
		r = subprocess.call([build_script_file])
	else:
		build_script_contents = "# Autogenerated by mibuild\nset -e\n"
		settings = common.settings(vivado_path, ver)
		build_script_contents += "source " + settings + "\n"
		build_script_contents += "vivado -mode batch -source " + build_name + ".tcl\n"
		build_script_file = "build_" + build_name + ".sh"
		tools.write_to_file(build_script_file, build_script_contents)
		r = subprocess.call(["bash", build_script_file])

	if r != 0:
		raise OSError("Subprocess failed")

class XilinxVivadoToolchain:
	def __init__(self):
		self.bitstream_commands = []
		self.additional_commands = []
		self.pre_synthesis_commands = []
		self.with_phys_opt = False

	def _build_batch(self, platform, sources, build_name):
		tcl = []
		for filename, language in sources:
			tcl.append("add_files " + filename.replace("\\", "/"))

		tcl.append("read_xdc %s.xdc" %build_name)
		tcl.extend(c.format(build_name=build_name) for c in self.pre_synthesis_commands)
		tcl.append("synth_design -top top -part %s -include_dirs {%s}" %(platform.device, " ".join(platform.verilog_include_paths)))
		tcl.append("report_utilization -hierarchical -file %s_utilization_hierarchical_synth.rpt" %(build_name))
		tcl.append("report_utilization -file %s_utilization_synth.rpt" %(build_name))
		tcl.append("place_design")
		if self.with_phys_opt:
			tcl.append("phys_opt_design -directive AddRetime")
		tcl.append("report_utilization -hierarchical -file %s_utilization_hierarchical_place.rpt" %(build_name))
		tcl.append("report_utilization -file %s_utilization_place.rpt" %(build_name))
		tcl.append("report_io -file %s_io.rpt" %(build_name))
		tcl.append("report_control_sets -verbose -file %s_control_sets.rpt" %(build_name))
		tcl.append("report_clock_utilization -file %s_clock_utilization.rpt" %(build_name))
		tcl.append("route_design")
		tcl.append("report_route_status -file %s_route_status.rpt" %(build_name))
		tcl.append("report_drc -file %s_drc.rpt" %(build_name))
		tcl.append("report_timing_summary -max_paths 10 -file %s_timing.rpt" %(build_name))
		tcl.append("report_power -file %s_power.rpt" %(build_name))
		for bitstream_command in self.bitstream_commands:
			tcl.append(bitstream_command.format(build_name=build_name))
		tcl.append("write_bitstream -force %s.bit " %build_name)
		for additional_command in self.additional_commands:
			tcl.append(additional_command.format(build_name=build_name))
		tcl.append("quit")
		tools.write_to_file(build_name + ".tcl", "\n".join(tcl))

	def build(self, platform, fragment, build_dir="build", build_name="top",
			vivado_path="/opt/Xilinx/Vivado", source=True, run=True):
		tools.mkdir_noerror(build_dir)
		os.chdir(build_dir)

		if not isinstance(fragment, _Fragment):
			fragment = fragment.get_fragment()
		platform.finalize(fragment)
		v_src, vns = platform.get_verilog(fragment)
		named_sc, named_pc = platform.resolve_signals(vns)
		v_file = build_name + ".v"
		tools.write_to_file(v_file, v_src)
		sources = platform.sources | {(v_file, "verilog")}
		self._build_batch(platform, sources, build_name)
		tools.write_to_file(build_name + ".xdc", _build_xdc(named_sc, named_pc))
		if run:
			_run_vivado(build_name, vivado_path, source)

		os.chdir("..")

		return vns

	def add_period_constraint(self, platform, clk, period):
		platform.add_platform_command("""create_clock -name {clk} -period """ + \
			str(period) + """ [get_ports {clk}]""", clk=clk)
