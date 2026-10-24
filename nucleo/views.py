from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, timedelta
from nucleo.models import Colaborador, Emprestimo, EPI, Item

def home(request):
    return render(request, 'nucleo/home.html')

def equipamentos(request):
    if request.method == 'POST':
        id_editar = request.POST.get('id_editar')
        nome = request.POST.get('nome')
        num_estoque = request.POST.get('num_estoque')
        
        if id_editar:
            EPI.objects.filter(id=id_editar).update(nome=nome, estoque=num_estoque)
            messages.success(request, 'EPI atualizado com sucesso!')
        elif nome and num_estoque:
            EPI.objects.create(nome=nome, estoque=num_estoque) 
            messages.success(request, 'EPI cadastrado com sucesso!')
        else:
            messages.error(request, 'Erro: Preencha todos os campos.')
        return redirect('equipamentos')
    
    busca = request.GET.get('busca', '')
    editar_id = request.GET.get('editar') 
    obj_editar = EPI.objects.get(id=editar_id) if editar_id else None

    lista = EPI.objects.filter(nome__icontains=busca) if busca else EPI.objects.all()
    return render(request, 'nucleo/equipamentos.html', {'equipamentos': lista, 'obj_editar': obj_editar})

def colaboradores(request):
    if request.method == 'POST':
        id_editar = request.POST.get('id_editar')
        nome = request.POST.get('nome')
        matricula = request.POST.get('matricula')
        setor = request.POST.get('setor')
        
        if id_editar:
            Colaborador.objects.filter(id=id_editar).update(nome=nome, matricula=matricula, setor=setor)
            messages.success(request, 'Colaborador atualizado com sucesso!')
        elif nome and matricula and setor:
            Colaborador.objects.create(nome=nome, matricula=matricula, setor=setor)
            messages.success(request, 'Colaborador cadastrado!')
        else:
            messages.error(request, 'Erro: Preencha todos os campos.')
        return redirect('colaboradores')
    
    busca = request.GET.get('busca', '')
    editar_id = request.GET.get('editar') 
    obj_editar = Colaborador.objects.get(id=editar_id) if editar_id else None

    lista = Colaborador.objects.filter(nome__icontains=busca) if busca else Colaborador.objects.all()
    return render(request, 'nucleo/colaboradores.html', {'colaboradores': lista, 'obj_editar': obj_editar})

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
            id_editar = request.POST.get('id_editar')
            epi_id = request.POST.get('epi')
            colaborador_id = request.POST.get('colaborador')
            
            if id_editar:
                item = Item.objects.get(id=id_editar)
                novo_epi = EPI.objects.get(id=epi_id)
                novo_colab = Colaborador.objects.get(id=colaborador_id)
                
                if item.epi.id != novo_epi.id:
                    if novo_epi.estoque > 0:
                        item.epi.estoque += 1
                        item.epi.save()
                        novo_epi.estoque -= 1
                        novo_epi.save()
                        item.epi = novo_epi
                        item.save()
                    else:
                        messages.error(request, 'Erro: O novo EPI não possui estoque!')
                        return redirect('controle')
                
                item.emprestimo.colaborador = novo_colab
                item.emprestimo.save()
                messages.success(request, 'Empréstimo atualizado com sucesso!')
                
            elif epi_id and colaborador_id:
                epi = EPI.objects.get(id=epi_id)
                colaborador = Colaborador.objects.get(id=colaborador_id)
                
                if epi.estoque > 0:
                    novo_emprestimo = Emprestimo.objects.create(
                        colaborador=colaborador, status="Emprestado",
                        data_retirada=date.today(), data_devolucao_previsao=date.today() + timedelta(days=7)
                    )
                    Item.objects.create(emprestimo=novo_emprestimo, epi=epi, quantidade=1)
                    epi.estoque -= 1
                    epi.save()
                    messages.success(request, 'Empréstimo registrado com sucesso!')
                else:
                    messages.error(request, 'Erro: O EPI não possui estoque!')
            return redirect('controle')

    busca = request.GET.get('busca', '')
    editar_id = request.GET.get('editar') 
    obj_editar = Item.objects.get(id=editar_id) if editar_id else None

    lista_itens = Item.objects.filter(emprestimo__colaborador__nome__icontains=busca) if busca else Item.objects.all()

    return render(request, 'nucleo/controle.html', {
        'epis': EPI.objects.all(), 'colaboradores': Colaborador.objects.all(), 
        'emprestimos': lista_itens, 'obj_editar': obj_editar
    })

def excluir_colaborador(request, id):
    Colaborador.objects.get(id=id).delete()
    messages.success(request, 'Colaborador excluído com sucesso!')
    return redirect('colaboradores')

def excluir_epi(request, id):
    EPI.objects.get(id=id).delete()
    messages.success(request, 'EPI excluído com sucesso!')
    return redirect('equipamentos')

def excluir_emprestimo(request, id):
    item = Item.objects.get(id=id)
    if item.emprestimo.status in ['Emprestado', 'Atrasado']:
        item.epi.estoque += 1
        item.epi.save()
        
    item.emprestimo.delete()
    messages.success(request, 'Registro apagado com sucesso!')
    return redirect('controle')

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