# Evaluation policy

The current videos are supplemental training/diversity material. They are not
an acceptance benchmark because they do not provide a fixed camera, documented
counting line, or manually reviewed ground truth for every crossing.

Before a vision adapter is accepted:

1. Capture a representative fixed-view warehouse video.
2. Define the counting line, object classes, and event protocol.
3. Produce an independent manual ground-truth ledger.
4. Split evaluation footage from training footage by source and time.
5. Set an agreed error threshold and report false positives, false negatives,
   duplicate events, and unknown cases.

The current YOLO result is a comparison baseline only, not production accuracy.
