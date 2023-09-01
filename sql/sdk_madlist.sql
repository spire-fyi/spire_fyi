select
    *
from
    solana.nft.fact_nft_mints
where
    mint in ({% for item in mints -%}
        {% if loop.last -%}
            '{{ item }}'
        {% else %}
            '{{ item }}',
        {%- endif %}
    {%- endfor %})
order by
    block_timestamp