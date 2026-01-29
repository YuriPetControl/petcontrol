# 🚀 Configuração do Supabase para PetControl

## 📋 Passo a Passo

### 1. Criar Tabelas no Supabase

1. Acesse seu projeto no Supabase: https://yxrlxgvikzxuybvzxkmv.supabase.co
2. Vá em **SQL Editor**
3. Clique em **New Query**
4. Copie TODO o conteúdo do arquivo `supabase_schema.sql`
5. Cole no editor e clique em **Run**
6. Aguarde a execução (deve ver "Success" para cada comando)

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar WhatsApp

Abra o `app.py` e na linha 32, altere o número do WhatsApp:

```python
WHATSAPP_NUMERO = '5511999999999'  # Seu número no formato: código do país + DDD + número
```

Exemplo: Para (11) 98765-4321, use `5511987654321`

### 4. Próximos Passos da Implementação

O app.py já está preparado com:
- ✅ Conexão configurada com Supabase
- ✅ Funções CRUD (Create, Read, Update, Delete)
- ✅ Conversão automática de datas
- ✅ Tratamento de erros

**O que ainda precisa ser feito:**

1. **Modificar a inicialização dos dados** (linha ~225)
   - Substituir `st.session_state` por chamadas ao `supabase_get()`

2. **Modificar cada formulário de cadastro**
   - Substituir `.append()` por `supabase_post()`

3. **Modificar exibição de listas**
   - Buscar dados do Supabase ao invés de `session_state`

4. **Modificar botões de excluir**
   - Usar `supabase_delete()` ao invés de `.remove()`

5. **Modificar checkboxes de status**
   - Usar `supabase_update()` para atualizar o campo `concluido`

## 🔧 Estrutura das Tabelas Criadas

- **pets**: Dados dos pets cadastrados
- **vacinas**: Histórico de vacinas
- **alimentacao**: Planos alimentares
- **veterinario**: Consultas veterinárias
- **medicamentos**: Medicamentos ativos e finalizados
- **preventivos**: Antipulgas e vermífugos
- **peso**: Histórico de pesagens
- **notas**: Notas e observações

## 🎯 Exemplo de Uso

### Buscar todos os pets:
```python
pets = supabase_get('pets')
```

### Inserir novo pet:
```python
novo_pet = {
    'nome': 'Rex',
    'especie': 'Cão',
    'raca': 'Labrador',
    'data_nascimento': '2020-01-15',
    'peso': 25.5,
    'cor': 'Amarelo',
    'observacoes': 'Pet muito ativo'
}
resultado = supabase_post('pets', novo_pet)
```

### Atualizar pet:
```python
supabase_update('pets', pet_id, {'peso': 26.0})
```

### Deletar pet:
```python
supabase_delete('pets', pet_id)
```

## ⚠️ Importante

- As datas devem estar no formato ISO: `YYYY-MM-DD`
- Use a função `converter_data_para_string()` antes de enviar ao Supabase
- Sempre trate erros ao fazer operações no banco

## 📞 Suporte

Se precisar de ajuda, entre em contato ou revise a documentação do Supabase:
https://supabase.com/docs
