import os

path = r"c:\Users\preet\New folder (10)\app\main.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

target = """    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""

replacement = """    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))"""

if target in code:
    with open(path, "w", encoding="utf-8") as f:
        f.write(code.replace(target, replacement))
    print("Patched main.py")
else:
    print("Target not found")
