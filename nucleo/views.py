from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, timedelta
from nucleo.models import Colaborador, Emprestimo, EPI, Item

def home(request):
    return render(request, 'nucleo/home.html')

def equipamentos(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        num_estoque = request.POST.get('num_estoque')
        if nome and num_estoque:
            EPI.objects.create(nome=nome, estoque=num_estoque) 
            messages.success(request, 'EPI cadastrado com sucesso!')
        else:
            messages.error(request, 'Erro: Preencha todos os campos do EPI.')
        return redirect('equipamentos')
    
    busca = request.GET.get('busca', '')
    lista = EPI.objects.filter(nome__icontains=busca) if busca else EPI.objects.all()
    if busca and not lista:
        messages.error(request, 'Nenhum equipamento encontrado com este nome.')

    return render(request, 'nucleo/equipamentos.html', {'equipamentos': lista})

def colaboradores(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        matricula = request.POST.get('matricula')
        setor = request.POST.get('setor')
        if nome and matricula and setor:
            Colaborador.objects.create(nome=nome, matricula=matricula, setor=setor)
            messages.success(request, 'Colaborador cadastrado!')
        else:
            messages.error(request, 'Erro: Preencha todos os campos do colaborador.')
        return redirect('colaboradores')
    
    busca = request.GET.get('busca', '')
    lista = Colaborador.objects.filter(nome__icontains=busca) if busca else Colaborador.objects.all()
    if busca and not lista:
        messages.error(request, 'Nenhum colaborador encontrado.')

    return render(request, 'nucleo/colaboradores.html', {'colaboradores': lista})

def controle(request):
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'atualizar_status':
            item_id = request.POST.get('item_id')
            novo_status = request.POST.get('novo_status')
            
            item = Item.objects.get(id=item_id)
            emprestimo = item.emprestimo
            
            if emprestimo.status != novo_status:
                emprestimo.status = novo_status
                if novo_status == 'Devolvido':
                    emprestimo.data_devolucao = date.today()
                    item.epi.estoque += 1
                    item.epi.save()
                
                emprestimo.save()
                messages.success(request, f'Status atualizado para {novo_status} com sucesso!')
            
            return redirect('controle')
            
        else:
            epi_id = request.POST.get('epi')
            colaborador_id = request.POST.get('colaborador')
            
            if epi_id and colaborador_id:
                epi = EPI.objects.get(id=epi_id)
                colaborador = Colaborador.objects.get(id=colaborador_id)
                
                if epi.estoque > 0:
                    novo_emprestimo = Emprestimo.objects.create(
                        colaborador=colaborador,
                        status="Emprestado",
                        data_retirada=date.today(),
                        data_devolucao_previsao=date.today() + timedelta(days=7)
                    )
                    Item.objects.create(emprestimo=novo_emprestimo, epi=epi, quantidade=1)
                    
                    epi.estoque -= 1
                    epi.save()
                    
                    messages.success(request, f'EPI "{epi.nome}" emprestado para {colaborador.nome}! Estoque atualizado.')
                else:
                    messages.error(request, f'Erro: O EPI "{epi.nome}" não possui estoque!')
            else:
                messages.error(request, 'Erro: Selecione um Colaborador e EPI.')
            
            return redirect('controle')

    busca = request.GET.get('busca', '')
    if busca:
        lista_itens = Item.objects.filter(emprestimo__colaborador__nome__icontains=busca)
        if not lista_itens:
            messages.error(request, 'Nenhum registro encontrado para a busca.')
    else:
        lista_itens = Item.objects.all()

    return render(request, 'nucleo/controle.html', {
        'epis': EPI.objects.all(), 
        'colaboradores': Colaborador.objects.all(),
        'emprestimos': lista_itens
    })

def relatorios(request):
    lista_itens = Item.objects.all()
    qtd_emprestimos = Emprestimo.objects.filter(status="Emprestado").count()
    qtd_devolucoes = Emprestimo.objects.filter(status="Devolvido").count()
    qtd_atrasos = Emprestimo.objects.filter(status="Atrasado").count()

    return render(request, 'nucleo/relatorios.html', {
        'emprestimos': lista_itens,
        'qtd_emprestimos': qtd_emprestimos,
        'qtd_devolucoes': qtd_devolucoes,
        'qtd_atrasos': qtd_atrasos,
    })