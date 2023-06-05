from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from django.core.paginator import Paginator

from ..forms import CommentForm
from ..models import Question, Answer, Comment

@login_required(login_url='common:login')
def comment_create_question(request, question_id):
    """
    pybo 질문댓글등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.question = question
            comment.save()
            return redirect('{}#comment_{}'.format(
                resolve_url('pybo:detail', question_id=comment.question.id), comment.id))
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='common:login')
def comment_modify_question(request, comment_id):
    """
    pybo 질문댓글수정
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.question.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.modify_count += 1
            comment.save()
            return redirect('{}#comment_{}'.format(
                resolve_url('pybo:detail', question_id=comment.question.id), comment.id))
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='common:login')
def comment_delete_question(request, comment_id):
    """
    pybo 질문댓글삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.question_id)
    else:
        comment.delete()
    return redirect('pybo:detail', question_id=comment.question_id)

@login_required(login_url='common:login')
def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    page = request.GET.get('page', '1')  # 페이지
    comments = Comment.objects.filter(question=question).order_by('create_date')
    paginator = Paginator(comments, 5)  # 페이지당 5개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'question': question, 'comments_page': page_obj}
    return render(request, 'pybo/question_detail.html', context)

    # question = get_object_or_404(Question, pk=question_id)
    # comments = Comment.objects.filter(question=question).order_by('create_date')
    #
    # paginator = Paginator(comments, 5)
    # page = request.GET.get('page', 1)
    # comments_page = paginator.get_page(page)
    # comments_list = question.comment_set.all()
    # context = {'question': question, 'comments_page': comments_page, 'comments_list':comments_list}
    # return render(request, 'pybo/question_detail.html', context)