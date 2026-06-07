# MOST 3D Streamlit Demo

Run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Recommended model format: `.glb` under 25 MB.

If you have a Mixamo `.fbx`, convert it in Blender:

1. File > Import > FBX
2. File > Export > glTF 2.0
3. Format: GLB
4. Optional: reduce mesh/texture size before export

Large FBX files can crash the browser because they are decoded in memory.
