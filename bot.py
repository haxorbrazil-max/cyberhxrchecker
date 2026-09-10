import random,string
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder,CommandHandler,CallbackQueryHandler,MessageHandler,ContextTypes,filters
from config import BOT_TOKEN,ADMIN_ID
from database import connect,init_db
from utils import money_to_cents,money,stock_fields
from pluspix import create_deposit,check_transaction

def admin(u): return u.effective_user.id==ADMIN_ID

async def start(u,c):
    x=u.effective_user; db=connect(); db.execute('INSERT OR IGNORE INTO users(user_id,name,username) VALUES(?,?,?)',(x.id,x.full_name,x.username)); db.commit(); db.close()
    kb=[[InlineKeyboardButton('🛍️ Produtos',callback_data='products')],[InlineKeyboardButton('💰 Saldo',callback_data='balance')],[InlineKeyboardButton('➕ Depositar PIX',callback_data='deposit')],[InlineKeyboardButton('🎁 Resgatar Gift',callback_data='redeem')]]
    await u.message.reply_text('🛍️ Loja Digital\n\nEscolha uma opção:',reply_markup=InlineKeyboardMarkup(kb))

async def saldo(u,c):
    db=connect(); r=db.execute('SELECT balance_cents FROM users WHERE user_id=?',(u.effective_user.id,)).fetchone(); db.close()
    await u.message.reply_text('💰 Saldo: '+money(r['balance_cents'] if r else 0))

async def products(u,c):
    db=connect(); rows=db.execute('SELECT * FROM products WHERE enabled=1').fetchall(); db.close()
    if not rows: return await u.message.reply_text('Nenhum produto disponível.')
    await u.message.reply_text('\n\n'.join(f"#{r['id']} — {r['name']}\n{r['category']} | {money(r['price_cents'])}\n{r['description']}" for r in rows))

async def addproduct(u,c):
    if not admin(u): return
    p=[x.strip() for x in u.message.text.partition(' ')[2].split('|')]
    if len(p)!=4: return await u.message.reply_text('Uso: /addproduct CATEGORIA|NOME|DESCRIÇÃO|PREÇO')
    try: cents=money_to_cents(p[3])
    except: return await u.message.reply_text('Preço inválido.')
    db=connect(); q=db.execute('INSERT INTO products(category,name,description,price_cents) VALUES(?,?,?,?)',(p[0],p[1],p[2],cents)); db.commit(); db.close()
    await u.message.reply_text(f'✅ Produto #{q.lastrowid} criado.')

async def addstock(u,c):
    if not admin(u): return
    try: v=stock_fields(u.message.text.partition(' ')[2])
    except ValueError as e: return await u.message.reply_text('❌ '+str(e))
    db=connect(); q=db.execute('INSERT INTO stock(identifier,code5,code34,fictional_name,number10,value_cents) VALUES(?,?,?,?,?,?)',v); db.commit(); db.close()
    await u.message.reply_text(f'✅ Estoque #{q.lastrowid} adicionado.')

async def stock(u,c):
    if not admin(u): return
    db=connect(); rows=db.execute('SELECT * FROM stock ORDER BY id DESC').fetchall(); db.close()
    await u.message.reply_text('\n'.join(f"#{r['id']} | {r['identifier']} | {money(r['value_cents'])} | {'VENDIDO' if r['sold'] else 'DISPONÍVEL'}" for r in rows) or 'Estoque vazio.')

async def giftcreate(u,c):
    if not admin(u) or len(c.args)!=1: return
    try: cents=money_to_cents(c.args[0])
    except: return await u.message.reply_text('Valor inválido.')
    code=''.join(random.choices(string.ascii_uppercase+string.digits,k=12))
    db=connect(); db.execute('INSERT INTO gifts(code,value_cents) VALUES(?,?)',(code,cents)); db.commit(); db.close()
    await u.message.reply_text(f'🎁 Gift: `{code}` — {money(cents)}',parse_mode='Markdown')

async def callbacks(u,c):
    q=u.callback_query; await q.answer()
    if q.data=='products': return await q.message.reply_text('Use /products')
    if q.data=='balance': return await saldo(Update(update_id=0,message=q.message),c)
    if q.data=='deposit':
        c.user_data['deposit']=True; return await q.message.reply_text('Envie o valor do depósito. Ex: 50.00')
    if q.data=='redeem':
        c.user_data['redeem']=True; return await q.message.reply_text('Envie o código do Gift Card.')

async def text(u,c):
    uid=u.effective_user.id; t=u.message.text.strip()
    if c.user_data.pop('redeem',False):
        db=connect(); r=db.execute('SELECT value_cents FROM gifts WHERE code=? AND used=0',(t,)).fetchone()
        if not r: db.close(); return await u.message.reply_text('❌ Gift inválido.')
        db.execute('UPDATE gifts SET used=1 WHERE code=? AND used=0',(t,)); db.execute('UPDATE users SET balance_cents=balance_cents+? WHERE user_id=?',(r['value_cents'],uid)); db.commit(); db.close()
        return await u.message.reply_text('✅ Crédito: '+money(r['value_cents']))
    if c.user_data.pop('deposit',False):
        try: cents=money_to_cents(t)
        except: return await u.message.reply_text('Valor inválido.')
        try: data=create_deposit(cents,f'Depósito Telegram {uid}')
        except Exception as e: return await u.message.reply_text('❌ Erro ao criar PIX: '+str(e))
        tid=data.get('transactionId'); db=connect(); db.execute('INSERT OR IGNORE INTO transactions(user_id,provider_transaction_id,amount_cents,state) VALUES(?,?,?,?)',(uid,tid,cents,'PENDENTE')); db.commit(); db.close()
        msg=f"💳 PIX criado\nValor: {money(cents)}\nID: `{tid}`"
        if data.get('qrcodeUrl'): msg+='\nQR Code: '+data['qrcodeUrl']
        if data.get('copyPaste'): msg+='\nPix Copia e Cola:\n`'+data['copyPaste']+'`'
        return await u.message.reply_text(msg,parse_mode='Markdown')

async def check(u,c):
    if not c.args: return await u.message.reply_text('Uso: /check TRANSACTION_ID')
    tid=c.args[0]; db=connect(); local=db.execute('SELECT * FROM transactions WHERE provider_transaction_id=? AND user_id=?',(tid,u.effective_user.id)).fetchone(); db.close()
    if not local: return await u.message.reply_text('❌ Transação não encontrada.')
    try: d=check_transaction(tid)
    except Exception as e: return await u.message.reply_text('❌ Erro PlusPix: '+str(e))
    x=d.get('transaction',d); state=str(x.get('transactionState','')).upper(); typ=str(x.get('transactionType','')).upper()
    if state!='COMPLETO' or typ!='DEPOSITO': return await u.message.reply_text('⏳ Status: '+(state or 'DESCONHECIDO'))
    if int(round(float(x.get('value'))*100))!=local['amount_cents']: return await u.message.reply_text('❌ Valor divergente.')
    db=connect(); db.execute('BEGIN IMMEDIATE'); r=db.execute('SELECT credited FROM transactions WHERE id=?',(local['id'],)).fetchone()
    if r['credited']: db.commit(); db.close(); return await u.message.reply_text('✅ Já creditado.')
    db.execute('UPDATE users SET balance_cents=balance_cents+? WHERE user_id=?',(local['amount_cents'],local['user_id'])); db.execute('UPDATE transactions SET state=?,transaction_type=?,credited=1 WHERE id=?',('COMPLETO','DEPOSITO',local['id'])); db.commit(); db.close()
    await u.message.reply_text('✅ Pagamento confirmado e saldo creditado: '+money(local['amount_cents']))

def main():
    init_db(); a=ApplicationBuilder().token(BOT_TOKEN).build()
    for cmd,fn in [('start',start),('saldo',saldo),('products',products),('addproduct',addproduct),('addstock',addstock),('stock',stock),('giftcreate',giftcreate),('check',check)]:
        a.add_handler(CommandHandler(cmd,fn))
    a.add_handler(CallbackQueryHandler(callbacks)); a.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text)); a.run_polling()
if __name__=='__main__': main()
