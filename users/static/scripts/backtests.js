const strategySelect = document.getElementById('strategy');
    strategySelect.addEventListener('change', () => {
        document.getElementById('strategy-form').submit();
    });

const strategyParams = document.getElementsByClassName('strategy-params');
    strategySelect.addEventListener('change', () => {
        const selectedStrategy = strategySelect.value;
        Array.from(strategyParams).forEach(params => {
            params.style.display = (params.id === `${selectedStrategy}-params`) ? 'block' : 'none';
        });
        document.getElementById('strategy-form').submit();
    });