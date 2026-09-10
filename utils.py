from decimal import Decimal
def money_to_cents(v):
    x=Decimal(v.replace(',','.'))
    if x<=0: raise ValueError("valor deve ser maior que zero")
    return int(x*100)
def money(c): return f"R$ {c/100:.2f}"
def stock_fields(raw):
    p=[x.strip() for x in raw.split('|')]
    if len(p)!=6: raise ValueError("use 6 campos separados por |")
    a,b,d,n,e,v=p
    if not a.isdigit() or not 12<=len(a)<=16: raise ValueError("identificador: 12-16 dígitos")
    if len(b)!=5: raise ValueError("código: 5 caracteres")
    if not d.isdigit() or len(d) not in (3,4): raise ValueError("código: 3-4 números")
    if not n: raise ValueError("nome fictício obrigatório")
    if not e.isdigit() or len(e)!=10: raise ValueError("número: 10 dígitos")
    return a,b,d,n,e,money_to_cents(v)
