document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');
    const strategySelect = document.getElementById('strategy');
    const strategyParams = document.getElementsByClassName('strategy-params');

    strategySelect.addEventListener('change', () => {
        const selectedStrategy = strategySelect.value;
        Array.from(strategyParams).forEach(params => {
            if (params.id === `${selectedStrategy}-params`) {
                params.style.display = 'block';
            } else {
                params.style.display = 'none';
            }
        });
    });
});