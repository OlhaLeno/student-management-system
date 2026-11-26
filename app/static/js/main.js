function showError(message) {
    const alert = document.getElementById('api-message');
    alert.textContent = message;
    alert.className = 'alert alert-danger';
    alert.scrollIntoView({block: 'nearest'});
}

async function sendRequest(url, method, data) {
    const options = {method: method};
    if (data !== undefined) {
        options.headers = {'Content-Type': 'application/json'};
        options.body = JSON.stringify(data);
    }
    const response = await fetch(url, options);
    if (!response.ok) {
        const result = await response.json().catch(() => ({}));
        throw new Error(result.error || `Помилка запиту (${response.status}).`);
    }
}

async function saveAndReload(url, method, data, button) {
    button.disabled = true;
    try {
        await sendRequest(url, method, data);
        window.location.reload();
    } catch (error) {
        showError(error.message);
        button.disabled = false;
    }
}

document.querySelectorAll('form[data-api]').forEach(form => {
    form.addEventListener('submit', event => {
        event.preventDefault();
        const data = {};
        for (const [name, value] of new FormData(form)) {
            const field = form.elements.namedItem(name);
            data[name] = field.type === 'number' || field.hasAttribute('data-number')
                ? Number(value) : value.trim();
        }
        const id = form.dataset.editId;
        const method = id ? 'PUT' : 'POST';
        const url = form.dataset.api + (id ? '/' + id : '');
        saveAndReload(url, method, data, form.querySelector('[type="submit"]'));
    });

    form.querySelector('[data-cancel]').addEventListener('click', () => {
        form.reset();
        if (form.id === 'schedule-form') {
            updateScheduleSubjects();
            updateScheduleTimes();
        }
        delete form.dataset.editId;
        form.querySelector('[type="submit"]').textContent = 'Додати';
        form.querySelector('[data-cancel]').classList.add('d-none');
    });
});

document.querySelectorAll('[data-edit]').forEach(button => {
    button.addEventListener('click', () => {
        const form = document.getElementById(button.dataset.edit);
        const record = JSON.parse(button.dataset.record);
        for (const field of form.elements) {
            if (field.name && Object.hasOwn(record, field.name)) {
                field.value = record[field.name];
            }
        }
        if (form.id === 'schedule-form') {
            updateScheduleSubjects();
            form.elements.subject_id.value = record.subject_id;
            selectScheduleSlot(record.start_time, record.end_time);
        }
        form.dataset.editId = record.id;
        form.querySelector('[type="submit"]').textContent = 'Зберегти';
        form.querySelector('[data-cancel]').classList.remove('d-none');
        form.scrollIntoView({block: 'nearest'});
        form.querySelector('input')?.focus();
    });
});

document.querySelectorAll('[data-delete]').forEach(button => {
    button.addEventListener('click', () => {
        const message = button.dataset.deleteConfirm
            || 'Ви впевнені, що хочете видалити цей запис?';
        if (window.confirm(message)) {
            saveAndReload(button.dataset.delete, 'DELETE', undefined, button);
        }
    });
});

const assignmentForm = document.getElementById('assignment-form');
if (assignmentForm) {
    assignmentForm.addEventListener('submit', event => {
        event.preventDefault();
        const groupId = assignmentForm.elements.group_id.value;
        const subjectId = assignmentForm.elements.subject_id.value;
        saveAndReload(`/api/groups/${groupId}/subjects/${subjectId}`, 'PUT',
            undefined, assignmentForm.querySelector('[type="submit"]'));
    });
}

const studentSearch = document.getElementById('student-search');
const groupFilter = document.getElementById('group-filter');
if (studentSearch && groupFilter) {
    const rows = document.querySelectorAll('#students-table tbody tr[data-student-name]');
    function filterStudents() {
        const query = studentSearch.value.trim().toLocaleLowerCase('uk');
        let visible = 0;
        rows.forEach(row => {
            const nameMatches = row.dataset.studentName.toLocaleLowerCase('uk').includes(query);
            const groupMatches = !groupFilter.value || row.dataset.groupId === groupFilter.value;
            row.hidden = !(nameMatches && groupMatches);
            if (!row.hidden) visible++;
        });
        document.getElementById('student-no-results').classList.toggle('d-none', visible > 0 || rows.length === 0);
    }
    studentSearch.addEventListener('input', filterStudents);
    groupFilter.addEventListener('change', filterStudents);

    const resetButton = document.getElementById('student-filter-reset');

    if (resetButton) {
        resetButton.addEventListener('click', () => {
            studentSearch.value = '';
            groupFilter.value = '';
            filterStudents();
        });
    }
}

function filterSubjects(select, groupId) {
    for (const option of select.options) {
        if (!option.value) continue;
        const available = Boolean(groupId) && option.dataset.groups.split(',').includes(groupId);
        option.hidden = !available;
        option.disabled = !available;
    }
    if (select.selectedOptions[0]?.disabled || !select.selectedOptions.length) {
        select.value = '';
    }
}

const scheduleForm = document.getElementById('schedule-form');
function updateScheduleSubjects() {
    filterSubjects(scheduleForm.elements.subject_id, scheduleForm.elements.group_id.value);
}
function updateScheduleTimes() {
    if (!scheduleForm) return;
    const slot = document.getElementById('schedule-slot').value;
    const [start, end] = slot ? slot.split('|') : ['', ''];
    scheduleForm.elements.start_time.value = start;
    scheduleForm.elements.end_time.value = end;
}

function selectScheduleSlot(start, end) {
    const select = document.getElementById('schedule-slot');
    const slot = `${String(start).slice(0, 5)}|${String(end).slice(0, 5)}`;
    select.value = Array.from(select.options).some(option => option.value === slot)
        ? slot : '';
    updateScheduleTimes();
}

if (scheduleForm) {
    scheduleForm.elements.group_id.addEventListener('change', updateScheduleSubjects);
    document.getElementById('schedule-slot').addEventListener('change', updateScheduleTimes);
    updateScheduleSubjects();
    updateScheduleTimes();
}

const gradeForm = document.getElementById('grade-form');
if (gradeForm) {
    const student = gradeForm.elements.student_id;
    const kind = gradeForm.elements.kind;
    const score = gradeForm.elements.score;
    const passed = gradeForm.elements.passed;

    function updateGradeSubjects() {
        filterSubjects(gradeForm.elements.subject_id, student.selectedOptions[0]?.dataset.group);
    }
    function updateGradeFields() {
        const exam = kind.value === 'exam';
        document.getElementById('exam-field').classList.toggle('d-none', !exam);
        document.getElementById('credit-field').classList.toggle('d-none', exam);
        score.disabled = !exam;
        score.required = exam;
        passed.disabled = exam;
        passed.required = !exam;
    }
    student.addEventListener('change', updateGradeSubjects);
    kind.addEventListener('change', updateGradeFields);
    updateGradeSubjects();
    updateGradeFields();

    gradeForm.addEventListener('submit', event => {
        event.preventDefault();
        const data = {
            student_id: Number(student.value),
            subject_id: Number(gradeForm.elements.subject_id.value),
            kind: kind.value
        };
        if (data.kind === 'exam') data.score = Number(score.value);
        else data.passed = passed.value === 'true';
        saveAndReload('/api/grades', 'POST', data, gradeForm.querySelector('[type="submit"]'));
    });
}

const subjectPerformanceForm = document.getElementById('subject-performance-form');
if (subjectPerformanceForm) {
    const subjectSelect = subjectPerformanceForm.elements.subject_id;
    const groupSelect = subjectPerformanceForm.elements.group_id;

    function updateSubjectPerformanceGroups(resetSelection = false) {
        const subjectId = subjectSelect.value;
        groupSelect.disabled = !subjectId;

        for (const option of groupSelect.options) {
            if (!option.value) continue;
            const subjectIds = (option.dataset.subjects || '').split(',');
            const available = Boolean(subjectId) && subjectIds.includes(subjectId);
            option.hidden = !available;
            option.disabled = !available;
        }

        if (resetSelection || groupSelect.selectedOptions[0]?.disabled) {
            groupSelect.value = '';
        }
    }

    subjectSelect.addEventListener('change', () => updateSubjectPerformanceGroups(true));
    updateSubjectPerformanceGroups();
}

const gradeEditForm = document.getElementById('grade-edit-form');
if (gradeEditForm) {
    const panel = document.getElementById('grade-edit-panel');
    const examField = document.getElementById('grade-edit-exam-field');
    const creditField = document.getElementById('grade-edit-credit-field');
    const editKind = document.getElementById('grade-edit-kind');
    const editScore = document.getElementById('grade-edit-score');
    const editPassed = document.getElementById('grade-edit-passed');

    function updateEditFields() {
        const isExam = editKind.value === 'exam';
        examField.classList.toggle('d-none', !isExam);
        creditField.classList.toggle('d-none', isExam);
        editScore.disabled = !isExam;
        editScore.required = isExam;
        editPassed.disabled = isExam;
        editPassed.required = !isExam;
    }

    editKind.addEventListener('change', updateEditFields);

    document.querySelectorAll('[data-grade-edit]').forEach(button => {
        button.addEventListener('click', () => {
            gradeEditForm.dataset.gradeId = button.dataset.gradeId;
            document.getElementById('grade-edit-description').textContent =
                `${button.dataset.gradeStudent} — ${button.dataset.gradeSubject}`;
            editKind.value = button.dataset.gradeKind;
            editScore.value = button.dataset.gradeScore;
            editPassed.value = button.dataset.gradePassed;
            updateEditFields();
            panel.classList.remove('d-none');
            panel.scrollIntoView({block: 'nearest'});
        });
    });

    document.getElementById('grade-edit-cancel').addEventListener('click', () => {
        panel.classList.add('d-none');
        gradeEditForm.reset();
        delete gradeEditForm.dataset.gradeId;
    });

    gradeEditForm.addEventListener('submit', event => {
        event.preventDefault();
        const id = gradeEditForm.dataset.gradeId;
        if (!id) return;

        const data = {kind: editKind.value};
        if (data.kind === 'exam') {
            if (editScore.value.trim() === '') {
                showError('Вкажіть оцінку за іспит.');
                return;
            }
            data.score = Number(editScore.value);
        } else {
            data.passed = editPassed.value === 'true';
        }
        saveAndReload(`/api/grades/${id}`, 'PUT', data,
            gradeEditForm.querySelector('[type="submit"]'));
    });
}

const notificationArea = document.getElementById('notification-area');
if (notificationArea) {
    const notificationToggle = document.getElementById('notification-toggle');
    const notificationMenu = document.getElementById('notification-menu');
    const notificationCount = document.getElementById('notification-count');
    const markAllButton = document.getElementById('notification-mark-all');

    let unreadCount = Number(notificationCount.dataset.unreadCount || 0);

    function setUnreadCount(count) {
        unreadCount = count;
        notificationCount.dataset.unreadCount = String(count);
        notificationCount.textContent = count > 99 ? '99+' : String(count);
        notificationCount.classList.toggle('d-none', count === 0);
        if (markAllButton) markAllButton.classList.toggle('d-none', count === 0);
    }

    async function markAsRead(item) {
        if (item.dataset.notificationRead === 'true') return;

        const response = await fetch(
            `/api/notifications/${item.dataset.notificationId}/read`,
            {method: 'PATCH'}
        );
        if (!response.ok) {
            const result = await response.json().catch(() => ({}));
            throw new Error(result.error || 'Не вдалося оновити сповіщення.');
        }

        item.dataset.notificationRead = 'true';
        item.classList.remove('unread');
        setUnreadCount(Math.max(0, unreadCount - 1));
    }

    notificationToggle.addEventListener('click', () => {
        const isOpening = notificationMenu.classList.contains('d-none');
        notificationMenu.classList.toggle('d-none');
        notificationToggle.setAttribute('aria-expanded', String(isOpening));
    });

    document.addEventListener('click', event => {
        if (!notificationArea.contains(event.target)) {
            notificationMenu.classList.add('d-none');
            notificationToggle.setAttribute('aria-expanded', 'false');
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            notificationMenu.classList.add('d-none');
            notificationToggle.setAttribute('aria-expanded', 'false');
        }
    });

    document.querySelectorAll('[data-notification-id]').forEach(item => {
        item.addEventListener('click', async () => {
            try {
                await markAsRead(item);
            } catch (error) {
                showError(error.message);
            }
        });
    });

    if (markAllButton) {
        markAllButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/notifications/read-all', {
                    method: 'PATCH'
                });
                if (!response.ok) {
                    const result = await response.json().catch(() => ({}));
                    throw new Error(result.error || 'Не вдалося оновити сповіщення.');
                }

                document.querySelectorAll('[data-notification-id]').forEach(item => {
                    item.dataset.notificationRead = 'true';
                    item.classList.remove('unread');
                });
                setUnreadCount(0);
            } catch (error) {
                showError(error.message);
            }
        });
    }
}
