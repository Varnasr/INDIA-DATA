// Links to the Bihar dashboard used to live at this address. Send them on.
(function () { var t = location.hash.slice(1); if (/^(overview|deletions|reasons|phases|gender|caste|religion|electoral|geographic|economic|research|methodology)$/.test(t)) location.replace('bihar/#' + t); })();
