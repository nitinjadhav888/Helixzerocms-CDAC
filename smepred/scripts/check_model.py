import pickle
import pathlib
import numpy as np

p = pathlib.Path("models/model_b.pkl")
m = pickle.loads(p.read_bytes())

print(f"Model type: {type(m).__name__}")
print(f"num_feature(): {m.num_feature()}")
imp = m.feature_importance()
print(f"feature_importance() len: {len(imp)}")
print(f"  min={imp.min()}, max={imp.max()}, nonzero={np.count_nonzero(imp)}")
print(f"  total importance sum: {imp.sum()}")

# Also check the training script to see what dimension it uses
