# B5 — Room-level localisation by metric learning

**Source:** internal I7 (metric-learning approach, network options, room-level training augmentation), generalised; Hadsell, Chopra, LeCun, CVPR 2006 (contrastive loss); Schroff, Kalenichenko, Philbin, CVPR 2015 (FaceNet, triplet loss). · **Status:** concept note, a proposed method. No result numbers are given in this note.

## In one sentence
A room classifier cannot move to a home with a different number of rooms, so instead you train a network that maps a CSI window to an embedding in which windows from the same room are close and windows from different rooms are far apart, then calibrate each new home with one walk through each room and answer "which room" by nearest neighbour.

## What it is
**Metric learning** trains a network to produce an **embedding** — a fixed-length vector — such that the distance between two embeddings reflects whether the two inputs belong together. The network learns a notion of similarity, not a fixed list of classes. The same idea underlies face verification: FaceNet learns one embedding for all faces, and a new person needs only a few reference photos (Schroff et al. 2015).

## How it works
**Why not a classifier.** A classifier has one output per class. Homes have different numbers of rooms and different layouts, so a room classifier trained on four-room homes has no meaning in a six-room home. It would need retraining per home with a large labelled dataset (internal I7).

**Training.** Use CSI windows from many homes, each labelled with the room where the person was.

- **Contrastive loss** takes pairs. It pulls embeddings of a same-room pair together and pushes a different-room pair apart until they are at least a margin away (Hadsell et al. 2006).
- **Triplet loss** takes an anchor, a positive from the same room, and a negative from a different room. It requires the anchor–negative distance to exceed the anchor–positive distance by a margin. FaceNet uses a margin of 0.2 on unit-length embeddings (`triplet_margin_facenet`; Schroff et al. 2015).
- One shared network embeds all inputs (a **Siamese** arrangement). Pairs or triplets are formed within one home, because "same room" has meaning only inside one home (my explanation).

**Calibration, once per home.** The user walks through each room once while the devices record CSI. The system embeds these windows and stores one or a few **reference embeddings** per room (internal I7).

**Inference.** Embed the live CSI window from all receivers. Find the nearest reference embedding. Return its room. A distance larger than every reference can mean "no one is in a calibrated room" or "the home has changed" (my explanation; see drift in [[C5-limits-and-open-problems]]).

**Network options.** Three feature-extractor designs were considered for a window shaped subcarriers × time (internal I7):

1. 1-D convolution along time, then a learned weighting over subcarriers;
2. 1-D convolution along time, then 1-D convolution along subcarriers, which assumes adjacent subcarriers are correlated (true, see [[B1-preprocessing]]);
3. 2-D convolution over the time–subcarrier matrix as an image.

**Training augmentation for single-device tests.** When the test must use only the AP link of one device, the training set can still include device-to-device links, if each is labelled by the room rule of [[B3-classifiers-and-windows]]. This adds training data without changing what is available at test time (internal I7).

**Room similarity for set-up.** The same embedding idea supports a simpler product feature: two devices whose CSI changes look alike are probably in the same room. This can assign smart-home devices to rooms automatically (internal I7).

## Common confusions
- **"The embedding learns the rooms of the training homes."** It should learn what makes two windows "same room", which transfers. The rooms of a new home enter only through calibration.
- **"One calibration walk lasts forever."** Furniture, doors, and device moves change the CSI. The reference embeddings age and need refresh (see [[C5-limits-and-open-problems]]).
- **"Metric learning removes the need for many homes."** It removes the need for labels *in the deployed home*. The embedding network still needs training data from many homes to generalise.
- **"Nearest neighbour always returns an answer."** Use a distance threshold so that the system can say "unknown".

## Why it matters
Room-level localisation is the use case that customers can act on ("turn off the lights in the empty room"). Metric learning turns a per-home classification problem, which does not scale, into a per-home calibration problem, which needs one walk. The cost moves from model retraining to a short user step.

## Terms introduced
- **metric learning** — training a network so that distances between its outputs encode similarity.
- **embedding** — the fixed-length vector a network produces for one input.
- **contrastive loss** — a pair loss that pulls similar pairs together and pushes dissimilar pairs at least a margin apart.
- **triplet loss** — a loss on (anchor, positive, negative) that requires the negative to be farther than the positive by a margin.
- **Siamese network** — one network with shared weights applied to every member of a pair or triplet.
- **calibration walk** — a one-time walk through each room to record reference CSI.
- **reference embedding** — a stored embedding that represents one room of one home.
- **nearest-neighbour decision** — returning the label of the closest reference embedding.
