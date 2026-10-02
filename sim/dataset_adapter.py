"""
Dataset adapter for importing and replaying synthetic RF emitter datasets (CSV / JSON).
Allows external scenarios and test vectors to be loaded directly into the RFEnvironment.
"""
import csv
import json
from typing import Dict, List, Any, Tuple
from .config import SimConfig
from .emitter import Emitter, FixedEmitter, PeriodicRadarEmitter, FrequencyAgileEmitter, DecoyEmitter
from .rf_environment import RFEnvironment


class DatasetAdapter:
    """Loads and serializes scenario datasets in CSV and JSON formats."""

    @staticmethod
    def load_from_json(json_str_or_dict: Any) -> RFEnvironment:
        """Parses a JSON dictionary or JSON string into an RFEnvironment."""
        if isinstance(json_str_or_dict, str):
            data = json.loads(json_str_or_dict)
        else:
            data = json_str_or_dict

        config_data = data.get("config", {})
        config = SimConfig(
            num_bands=config_data.get("num_bands", 16),
            freq_min_ghz=config_data.get("freq_min_ghz", 0.5),
            freq_max_ghz=config_data.get("freq_max_ghz", 18.0),
            dwell_time_ms=config_data.get("dwell_time_ms", 2.0),
            max_steps_per_episode=config_data.get("max_steps_per_episode", 350),
        )

        emitters: List[Emitter] = []
        for e in data.get("emitters", []):
            etype = e.get("emitter_type", "fixed").lower()
            eid = e.get("id", f"EM_{len(emitters)}")
            name = e.get("name", eid)
            priority = e.get("priority", 1)
            snr = float(e.get("base_snr_db", 18.0))
            start_step = e.get("start_step", 0)
            stop_step = e.get("stop_step", None)

            if etype == "fixed":
                emitters.append(
                    FixedEmitter(
                        id=eid,
                        name=name,
                        band=int(e.get("band", 0)),
                        duty_cycle=float(e.get("duty_cycle", 0.8)),
                        base_snr_db=snr,
                        priority=priority,
                        start_step=start_step,
                        stop_step=stop_step,
                    )
                )
            elif etype == "periodic":
                emitters.append(
                    PeriodicRadarEmitter(
                        id=eid,
                        name=name,
                        band=int(e.get("band", 0)),
                        scan_period=int(e.get("scan_period", 20)),
                        beam_width=int(e.get("beam_width", 2)),
                        phase_offset=int(e.get("phase_offset", 0)),
                        base_snr_db=snr,
                        priority=priority,
                        start_step=start_step,
                        stop_step=stop_step,
                    )
                )
            elif etype == "agile":
                hop_bands = [int(b) for b in e.get("hop_bands", [0, 1, 2])]
                emitters.append(
                    FrequencyAgileEmitter(
                        id=eid,
                        name=name,
                        hop_bands=hop_bands,
                        dwell_per_hop=int(e.get("dwell_per_hop", 1)),
                        hop_mode=e.get("hop_mode", "pseudorandom"),
                        base_snr_db=snr,
                        priority=priority,
                        start_step=start_step,
                        stop_step=stop_step,
                    )
                )
            elif etype == "decoy":
                emitters.append(
                    DecoyEmitter(
                        id=eid,
                        name=name,
                        band=int(e.get("band", 0)),
                        duty_cycle=float(e.get("duty_cycle", 0.95)),
                        base_snr_db=snr,
                        start_step=start_step,
                        stop_step=stop_step,
                    )
                )

        return RFEnvironment(config=config, emitters=emitters, seed=data.get("seed", 42))

    @staticmethod
    def load_from_csv(csv_text: str) -> RFEnvironment:
        """Parses CSV text containing emitter parameter specifications."""
        lines = [line.strip() for line in csv_text.strip().splitlines() if line.strip()]
        reader = csv.DictReader(lines)
        emitters: List[Emitter] = []
        max_band = 15

        for row in reader:
            eid = row.get("id", f"EM_{len(emitters)}")
            name = row.get("name", eid)
            etype = row.get("emitter_type", "fixed").strip().lower()
            snr = float(row.get("base_snr_db", 18.0))
            priority = int(row.get("priority", 1))
            start_step = int(row.get("start_step", 0))
            stop_str = row.get("stop_step")
            stop_step = int(stop_str) if stop_str and stop_str.isdigit() else None

            if etype == "fixed":
                band = int(row.get("band", 0))
                max_band = max(max_band, band)
                duty = float(row.get("duty_cycle", 0.8))
                emitters.append(
                    FixedEmitter(eid, name, band, duty_cycle=duty, base_snr_db=snr, priority=priority, start_step=start_step, stop_step=stop_step)
                )
            elif etype == "periodic":
                band = int(row.get("band", 0))
                max_band = max(max_band, band)
                period = int(row.get("scan_period", 20))
                beam = int(row.get("beam_width", 2))
                phase = int(row.get("phase_offset", 0))
                emitters.append(
                    PeriodicRadarEmitter(eid, name, band, scan_period=period, beam_width=beam, phase_offset=phase, base_snr_db=snr, priority=priority, start_step=start_step, stop_step=stop_step)
                )
            elif etype == "agile":
                hop_str = row.get("hop_bands", "0,1,2")
                hop_bands = [int(b.strip()) for b in hop_str.split(";") if b.strip()]
                for b in hop_bands:
                    max_band = max(max_band, b)
                dwell = int(row.get("dwell_per_hop", 1))
                emitters.append(
                    FrequencyAgileEmitter(eid, name, hop_bands, dwell_per_hop=dwell, base_snr_db=snr, priority=priority, start_step=start_step, stop_step=stop_step)
                )
            elif etype == "decoy":
                band = int(row.get("band", 0))
                max_band = max(max_band, band)
                emitters.append(
                    DecoyEmitter(eid, name, band, base_snr_db=snr, start_step=start_step, stop_step=stop_step)
                )

        num_bands = max(16, max_band + 1)
        config = SimConfig(num_bands=num_bands, max_steps_per_episode=350)
        return RFEnvironment(config=config, emitters=emitters, seed=42)

    @staticmethod
    def export_to_json(env: RFEnvironment) -> Dict[str, Any]:
        """Serializes an RFEnvironment instance to a JSON dictionary."""
        emitter_list = []
        for e in env.emitters:
            item = {
                "id": e.id,
                "name": e.name,
                "emitter_type": e.emitter_type,
                "priority": e.priority,
                "base_snr_db": e.base_snr_db,
                "start_step": e.start_step,
                "stop_step": e.stop_step,
            }
            if isinstance(e, (FixedEmitter, PeriodicRadarEmitter, DecoyEmitter)):
                item["band"] = getattr(e, "band", 0)
            if isinstance(e, FixedEmitter):
                item["duty_cycle"] = e.duty_cycle
            if isinstance(e, PeriodicRadarEmitter):
                item["scan_period"] = e.scan_period
                item["beam_width"] = e.beam_width
                item["phase_offset"] = e.phase_offset
            if isinstance(e, FrequencyAgileEmitter):
                item["hop_bands"] = e.hop_bands
                item["dwell_per_hop"] = e.dwell_per_hop
                item["hop_mode"] = e.hop_mode
            emitter_list.append(item)

        return {
            "config": {
                "num_bands": env.config.num_bands,
                "freq_min_ghz": env.config.freq_min_ghz,
                "freq_max_ghz": env.config.freq_max_ghz,
                "dwell_time_ms": env.config.dwell_time_ms,
                "max_steps_per_episode": env.config.max_steps_per_episode,
            },
            "seed": env.seed,
            "emitters": emitter_list,
        }
