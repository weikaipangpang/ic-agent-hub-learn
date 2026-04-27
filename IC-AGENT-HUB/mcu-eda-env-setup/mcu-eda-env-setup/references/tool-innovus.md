# Innovus Detection Template

name: innovus
vendor: Cadence
role: pnr
check_command: which innovus
version_command: innovus -version 2>&1 | head -1
module_name: (site-specific, e.g. innovus/<version> — read from project config modules.innovus)
binary: innovus

## Execution Pattern

floorplan: innovus -batch -files <tcl_script> -log <log_prefix>
place_route: innovus -batch -files <tcl_script> -log <log_prefix>
gds_export: innovus -batch -files <tcl_script> -log <log_prefix>
script_format: TCL (with separate MMMC view file)
execution_mode: async (floorplan, P&R), sync (GDS export)

## TCL Script Structure — Floorplan

1. Write MMMC view file (library sets, timing conditions, RC corners, delay corners, constraint modes, analysis views)
2. init_design with MMMC, netlist, LEF, power/ground nets
3. floorPlan -site <site> -d <width> <height> ...
4. Place SRAM macros (placeInstance)
5. addHaloToBlock
6. sroute (power routing)
7. addRing / addStripe (power distribution)
8. addWellTap / addEndCap
9. saveDesign

## TCL Script Structure — Place & Route

1. restoreDesign (from floorplan database)
2. setPlaceMode / place_opt_design
3. ccopt_design (CTS)
4. routeDesign
5. setAnalysisMode -analysisType onChipVariation
6. optDesign -postRoute
7. addFiller
8. ecoRoute (metal fill)
9. saveDesign + write outputs (netlist, DEF, SDC)
10. Reports: timing, hold, area, power, congestion, DRC

## MMMC Requirements

- SS corner (setup): slow .lib files + max TLU+
- FF corner (hold): fast .lib files + min TLU+
- Technology LEF + standard cell LEF + macro LEF

## Key Outputs

floorplan_db: <db_dir>/fp_db.dat
pnr_db: <db_dir>/pnr_db.dat
netlist: <output_dir>/<design>_final.v
def: <output_dir>/<design>_final.def
sdc: <output_dir>/<design>_final.sdc
gds: <gds_dir>/<design>.gds

## Physical Cell Requirements

filler_cells: from config (e.g. FILL64, FILL32, ..., FILL1)
tap_cell: from config
endcap_left: from config
endcap_right: from config

## Success Detection

Floorplan/P&R: database saved successfully
GDS: output file exists and log shows completion

## Clean

rm -rf <db_dir> <output_dir>/pnr* <rpt_dir>/pnr* <gds_dir>
