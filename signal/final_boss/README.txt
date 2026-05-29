GHOSTLIGHT PROTOCOL // FINAL BOSS
dead relay lab

boundary:
This is a fictional, offline, synthetic signal-forensics puzzle. Do not use real systems,
real sources, unauthorized access, real-time sources, or real-world collection attempts.

goal:
Recover the final_boss key. The final payload requires:

trunk::core::repair::aesthetic::body::mind::support::pets::creative::food::future::social::consent::final_boss

artifacts:
- pass_windows.csv
- burst_manifest.csv
- frame_notes.txt
- validator_hash.txt
- ../../tools/final_boss_validator.py

solve path:
1. Choose the one valid dead-lab pass.
   A valid pass has consent=Y, real_world_source=N, lab_lock=Y.
   Score remaining passes as:

   elevation_deg + snr_db - abs(drift_ppm)

   Select the highest score.

2. Use only rows in burst_manifest.csv with that pass_id.

3. Sort those rows by interleave_index, not by capture_slot.

4. Hex-decode the payload_hex values in sorted order.

5. Each byte is lab-masked. Unmask by XORing every byte with 0x13.

6. The result is the final_boss key.

7. Validate the recovered key:

   python tools/final_boss_validator.py <candidate_key>

8. If the validator accepts the key, use the accepted path format:

   signal/final_boss/accepted_<final_boss_key>.html

   plain text fallback:
   signal/final_boss/accepted_<final_boss_key>.txt

note:
This boss is meant to feel like hostile signal reconstruction while staying entirely
inside a made-up dataset.
