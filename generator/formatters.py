"""JavaScript formatter expressions evaluated by Pit House over `_result`.

Each is the second entry of a METHOD_CHAINING binding.
"""

# Copied verbatim from Pit House (base-template "Current gear").
GEAR = ("((r=Number(_result))=>{if(isNaN(r))return _result;else if(r==0)return'N';"
        "else if(r>0)return r.toString();else if(r==-1)return 'R';"
        "else if(r<-1)return 'R'+Math.abs(r).toString();})()")

PAD2 = "((r=Number(_result))=>isNaN(r)?'--':Math.max(0,Math.round(r)).toString().padStart(2,'0'))()"

INT = "((r=Number(_result))=>isNaN(r)?'-':Math.round(r).toString())()"

DELTA = "((r=Number(_result))=>isNaN(r)?'-.---':(r>0?'+':r<0?'-':'')+Math.abs(r).toFixed(3))()"

# Seconds -> m:ss.fff. Negative covers Pit House's no-data value (-3.4028234e+38).
LAPTIME = ("((r=Number(_result))=>{if(isNaN(r)||r<0)return'-:--.---';"
           "const t=Math.round(r*1000),m=Math.floor(t/60000),s=Math.floor(t/1000)%60,f=t%1000;"
           "return m+':'+String(s).padStart(2,'0')+'.'+String(f).padStart(3,'0');})()")

NAME = "((s=_result)=>s==null?'':String(s).toUpperCase())()"

# BrakeBias may arrive as a fraction (0.545) or a percentage (54.5).
BIAS = "((r=Number(_result))=>isNaN(r)?'--.-':(r<=1?r*100:r).toFixed(1))()"
